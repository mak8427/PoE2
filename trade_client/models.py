from typing import Any, Literal, Optional, TypedDict, TypeVar, Generic, List, Dict

class StatFilterValue(TypedDict, total=False):
    min: float
    max: float

class StatFilter(TypedDict):
    disabled: bool
    id: str  # e.g., pseudo.pseudo_adds_physical_damage
    value: StatFilterValue

StatFilterType = Literal["and", "if", "count", "weight"]

class QueryStat(TypedDict):
    disabled: bool
    filters: List[StatFilter]
    type: StatFilterType

OnlineStatus = Literal["online", "onlineleague", "any"]

class QueryStatus(TypedDict):
    option: OnlineStatus

class LinksFilter(TypedDict, total=False):
    a: Optional[int]
    b: Optional[int]
    d: Optional[int]
    g: Optional[int]
    max: Optional[int]
    min: Optional[int]
    r: Optional[int]
    w: Optional[int]

class SocketFilters(TypedDict, total=False):
    links: LinksFilter

class AccountFilter(TypedDict):
    input: str

class TradeFilters(TypedDict):
    account: AccountFilter

_TFilters = TypeVar("_TFilters")

class QueryFilter(TypedDict, Generic[_TFilters]):
    disabled: bool
    filters: _TFilters

class QueryFilters(TypedDict, total=False):
    socket_filters: QueryFilter[SocketFilters]
    trade_filters: QueryFilter[TradeFilters]

class TradeQuery(TypedDict):
    name: str
    stats: List[QueryStat]
    status: QueryStatus
    type: str
    filters: QueryFilters

SortPrice = Literal["asc"]  # Simplified for this example

class TradeSort(TypedDict):
    price: SortPrice

class TradeRequest(TypedDict):
    query: TradeQuery
    sort: TradeSort

class ListingStash(TypedDict):
    name: str
    x: int
    y: int

class ListingAccountOnline(TypedDict):
    league: str

class ListingAccount(TypedDict):
    name: str
    online: ListingAccountOnline | None
    language: str
    realm: str
    lastCharacterName: str
    current: bool

class ListingPrice(TypedDict):
    type: str
    amount: int
    currency: str

class ItemListing(TypedDict):
    method: str
    indexed: str
    stash: ListingStash
    account: ListingAccount
    price: ListingPrice
    whisper: str
    whisper_token: str

class ItemSocket(TypedDict):
    group: int
    attr: Literal["S", "D", "I", "G"]
    sColour: Literal["R", "G", "B", "W"]

class ItemProperty(TypedDict):
    name: str
    values: List[List[Any]]
    displayMode: int
    type: int

class ItemModMagnitude(TypedDict):
    hash: str
    min: int
    max: int

class ItemExtensionMod(TypedDict):
    name: str
    tier: str
    level: int
    magnitudes: List[ItemModMagnitude]

class ItemExtensionMods(TypedDict):
    explicit: List[ItemExtensionMod]
    implicit: List[ItemExtensionMod]

class ItemExtensionHashes(TypedDict):
    explicit: List[Any]  # actual structure is more complex
    implicit: List[Any]

class ItemExtension(TypedDict):
    dps: float
    pdps: float
    edps: float
    dps_aug: bool
    pdps_aug: bool
    mods: ItemExtensionMods
    hashes: ItemExtensionHashes
    text: str

class Item(TypedDict):
    verified: bool
    w: int
    h: int
    icon: str
    league: str
    id: str
    sockets: List[ItemSocket]
    name: str
    typeLine: str
    baseType: str
    identified: bool
    ilvl: int
    properties: List[ItemProperty]
    implicitMods: List[str]
    explicitMods: List[str]
    flavourText: List[str]
    frameType: int
    extended: ItemExtension

class SearchResult(TypedDict):
    id: str
    listing: ItemListing
    item: Item

class SearchResponse(TypedDict):
    """Send a POST with a TradeRequest to search"""
    id: str
    complexity: int
    result: List[str]
    total: int

class FetchResponse(TypedDict):
    """Send a GET request to fetch the search results"""
    result: List[SearchResult]

class Error(TypedDict):
    code: int
    message: str

class ErrorResponse(TypedDict):
    error: Error

class SuccessResponse(TypedDict):
    success: bool

WhisperResponse = SuccessResponse | ErrorResponse
