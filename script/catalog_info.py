from dataclasses import dataclass, field

@dataclass(frozen=True)
class catalog_info:
    pecha_id : str
    title : str 
    volume : any
    author : str 
    source_id : int 
    creation_date : str
    legacy_id : int
    
    
    
    