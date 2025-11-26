from typing import TypedDict, Dict, List

# Define the types for the YouTube API response
class Thumbnails(TypedDict):
    """
    the type for thumbnail session
    """
    url: str
    width: int
    height: int

class Snippet(TypedDict):
    """
    the type for the snippet
    """
    publishedAt: str
    channelId: str
    title: str
    description: str
    thumbnails: Dict[str, Thumbnails]
    channelTitle: str
    liveBroadcastContent: str
    publishTime: str

class VideoId(TypedDict):
    """
    the type for videoId
    """
    kind: str
    videoId: str

class Item(TypedDict):
    """
    the type for item 
    """
    kind: str
    etag: str
    id: VideoId
    snippet: Snippet

class PageInfo(TypedDict):
    """
    a type for the page info 
    """
    totalResults: int
    resultsPerPage: int

class YouTubeResponse(TypedDict):
    """
    the type for the youtube response 
    """
    kind: str
    etag: str
    nextPageToken: str
    regionCode: str
    pageInfo: PageInfo
    items: List[Item]
