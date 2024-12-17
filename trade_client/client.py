import json
import logging
from dataclasses import dataclass, field
from typing import Callable, TypeVar, List, Dict, Any

import requests
import websocket

from .models import (
    OnlineStatus,
    SortPrice,
    QueryStat,
    QueryFilters,
    TradeRequest,
    SearchResponse,
    FetchResponse,
    WhisperResponse,
    ItemListing,
)

@dataclass
class ClientConfig:
    league: str
    poesessid: str  # could be replaced with OAuth
    url: str = "https://www.pathofexile.com/api/trade2/"
    default_headers: Dict[str, str] = field(
        default_factory=lambda: {
            # have to fake the User-Agent to not get a 403
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
            "Accept": "*/*",
            "Content-Type": "application/json",
        }
    )
    log_level: int = logging.WARNING


@dataclass
class SearchConfig:
    item_name: str
    item_type: str
    online_opt: OnlineStatus = "online"
    price_sort: SortPrice = "asc"
    stat_filters: List[QueryStat] = field(
        default_factory=lambda: [{"type": "and", "filters": [], "disabled": False}]
    )
    query_filters: QueryFilters = field(default_factory=lambda: {})
    live: bool = False
    live_on_item_callback: Callable[[FetchResponse], None] | None = None


class TradeClient:
    _config: ClientConfig
    _sess: requests.Session | None = None
    _logger: logging.Logger

    def __init__(self, cfg: ClientConfig) -> None:
        self._config = cfg
        logging.basicConfig(level=cfg.log_level)
        self._logger = logging.getLogger("TradeClient")

    @property
    def config(self) -> ClientConfig:
        return self._config

    def _build_headers(self, extras: Dict[str, str] = {}) -> Dict[str, str]:
        # Create a copy of the default headers to avoid mutating the original
        h = {**self.config.default_headers, **extras}
        h["Cookie"] = f"POESESSID={self.config.poesessid}"
        return h

    def _build_search_url(self) -> str:
        return self.config.url + "search/" + self.config.league

    def _build_fetch_url(self, search_results: List[str]) -> str:
        return self.config.url + "fetch/" + ",".join(search_results)

    def _build_livesearch_url(self, query_id: str) -> str:
        return (
                self.config.url.replace("https", "wss")
                + f"live/{self.config.league}/{query_id}"
        )

    def _build_whisper_url(self) -> str:
        return self.config.url + "whisper"

    def _request(self, req: requests.Request, raise_error: bool = True) -> requests.Response:
        if not self._sess:
            self._sess = requests.Session()

        self._logger.debug(f"Request to send\n{req.__dict__}\n")
        res = self._sess.send(req.prepare(), allow_redirects=True)
        self._logger.debug(f"Full response {res.__dict__}")

        if raise_error:
            try:
                res.raise_for_status()
            except requests.HTTPError as e:
                self._logger.error(f"HTTPError: {e}")
                raise
        return res

    def _search(self, req: TradeRequest) -> SearchResponse:
        res = self._request(
            requests.Request(
                method="POST",
                url=self._build_search_url(),
                headers=self._build_headers(),
                data=json.dumps(req),
            )
        )
        return res.json()

    def _fetch(self, built_url: str, query_id: str) -> FetchResponse:
        res = self._request(
            requests.Request(
                method="GET",
                url=built_url,
                params={"query": query_id},
                headers=self._build_headers(),
            )
        )
        return res.json()

    def _whisper(self, whisper_token: str) -> WhisperResponse:
        res = self._request(
            requests.Request(
                method="POST",
                url=self._build_whisper_url(),
                data=json.dumps({"token": whisper_token}),
                headers=self._build_headers({"X-Requested-With": "XMLHttpRequest"}),
            ),
            raise_error=False,
        )
        # Not all responses might be JSON
        try:
            return res.json()
        except json.JSONDecodeError:
            self._logger.warning("Whisper response was not valid JSON.")
            return {"error": {"message": "Invalid JSON response"}}

    def _build_trade_request(self, cfg: SearchConfig) -> TradeRequest:
        return {
            "query": {
                "status": {"option": cfg.online_opt},
                "name": cfg.item_name,
                "type": cfg.item_type,
                "stats": cfg.stat_filters,
                "filters": cfg.query_filters,
            },
            "sort": {"price": cfg.price_sort},
        }

    _TPage = TypeVar("_TPage")

    def _build_pages(
            self, all_results: List[_TPage], page_width: int = 10
    ) -> List[List[_TPage]]:
        if len(all_results) <= page_width:
            return [all_results]

        pages: List[List[_TPage]] = []
        page: List[_TPage] = []
        for r in all_results:
            if len(page) < page_width:
                page.append(r)
            else:
                pages.append(page)
                page = [r]

        if page:  # append any leftover items
            pages.append(page)
        return pages

    def _build_ws_message_handler(
            self,
            search_id: str,
            fetch_callback: Callable[[FetchResponse], None] | None,
    ) -> Callable[[Any, str], None]:
        def on_message(ws: websocket.WebSocketApp, msg: str):
            self._logger.debug(f"Received msg {msg}")
            try:
                msg_data = json.loads(msg)
            except json.JSONDecodeError:
                self._logger.warning("Received invalid JSON message.")
                return

            if "new" in msg_data:
                new_item = msg_data["new"]
                fetch_res = self._fetch(self._build_fetch_url(new_item), search_id)
                if fetch_callback:
                    fetch_callback(fetch_res)
        return on_message

    def _normal_search(self, cfg: SearchConfig) -> FetchResponse:
        search_res = self._search(self._build_trade_request(cfg))
        if "result" not in search_res:
            self._logger.warning("Search returned no 'result' field.")
            return {"result": []}

        paged_ids = self._build_pages(search_res["result"])
        if not paged_ids:
            self._logger.info("No results for the given search.")
            return {"result": []}

        # Only going to show the first 10 results to avoid rate limiting
        fetch_res = self._fetch(self._build_fetch_url(paged_ids[0]), search_res["id"])
        return fetch_res

    def _live_search(self, cfg: SearchConfig) -> None:
        if self.config.log_level <= logging.DEBUG:
            websocket.enableTrace(True)

        # first have to get the search id
        search_id = self._search(self._build_trade_request(cfg))["id"]
        on_message = self._build_ws_message_handler(
            search_id, cfg.live_on_item_callback
        )

        wsapp = websocket.WebSocketApp(
            self._build_livesearch_url(search_id),
            on_open=lambda ws: self._logger.info(f"Starting livesearch for {cfg.item_name}"),
            on_message=on_message,
            header=self._build_headers(),
        )
        wsapp.run_forever()

    def search(self, cfg: SearchConfig) -> FetchResponse | None:
        if cfg.live:
            self._live_search(cfg)
            return None
        return self._normal_search(cfg)

    def whisper(self, listing: ItemListing) -> WhisperResponse:
        r = self._whisper(listing["whisper_token"])
        if "error" in r:
            self._logger.warning(f"Whisper error: {r['error']['message']}")  # type: ignore
        return r
