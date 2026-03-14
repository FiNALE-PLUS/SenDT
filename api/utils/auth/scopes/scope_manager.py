from enum import StrEnum
from typing import ClassVar
from warnings import deprecated

from pydantic import BaseModel


from api.utils.auth.scopes.fields.boolean_field import AdministratorScope, CrossEditScope, VerifyTwoFactorScope
from api.utils.auth.scopes.fields.db_access import DBRecordScopeField, ArtistScopeField, AudioScopeField, ChartCreatorScopeField, ChartScopeField, GenreScopeField, SdtBlobScopeField, SongScopeField, VideoScopeField
from api.utils.auth.scopes.fields.interface import ScopeField

class ScopeManager(BaseModel):
    """
    Manages the OAuth scopes of an authenticated user. Each field related to direct DB access manages its own sub-scopes, 
    which in turn authenticates a user's ability to interact with each type of content in a different way (read, write and delete at time of writing).
    This system intends to trade of immediate speed of directly adding a list of strings for scopes to validate in return for elimination of authentication bugs 
    related to accidentally mistyping a scope, and additionally easing the transition into adding new scopes when necessary.
    
    ``cross_edit_access`` is a special scope allowing for users to edit content submitted by another user (where as the API should otherwise enforce ownership for writes to a record).
    """

    allow_2fa_verification: VerifyTwoFactorScope   = VerifyTwoFactorScope()
    cross_edit_access:      CrossEditScope         = CrossEditScope()
    admin:                  AdministratorScope     = AdministratorScope()
    
    song_access:            SongScopeField         = SongScopeField()
    chart_access:           ChartScopeField        = ChartScopeField()
    artist_access:          ArtistScopeField       = ArtistScopeField()
    chart_creator_access:   ChartCreatorScopeField = ChartCreatorScopeField()
    genre_access:           GenreScopeField        = GenreScopeField()
    sdt_blob_access:        SdtBlobScopeField      = SdtBlobScopeField()
    audio_blob_access:      AudioScopeField        = AudioScopeField()
    video_blob_access:      VideoScopeField        = VideoScopeField()
    
    def match_token_string_scopes(self, token_scopes: str):
        # Reset permissions to then grant as found
        self.cross_edit_access = False
          
        # While the split isn't necessary as of writing, doing so now will prevent an accidental collision 
        # causing unwarranted permissions being given to users.
        
        # separate_scopes = token_scopes.split(' ')
        # if 'admin' in separate_scopes:
        #     self.admin = True
        # if 'xedit' in separate_scopes:
        #     self.cross_edit_access = True
        
        # Dynamically get all ``DBRecordScopeField``s, ensuring inclusion of any future fields as they are added
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, ScopeField), self.__pydantic_fields__.items()):
            scope_field: ScopeField = self.__getattribute__(field_name)
            scope_field.from_token_scope_string(token_scopes)
            

    def __str__(self):
        """
        Generates a string as expected by the ``scope`` field of a JWT.
        """        
        return ' '.join(self.get_scope_array())
    
    def get_scope_array(self):
        if self.admin:
            return self.admin.get_scope_values()
        
        access_fields = []
        
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, ScopeField), self.__pydantic_fields__.items()):
            stringified_scopes = self.__getattribute__(field_name).get_scope_values()
            if stringified_scopes is not None:
                access_fields.extend(stringified_scopes)
            
        return access_fields
    
    def get_openapi_scope_docs(self) -> dict[str, str]:
        docs_dict = {}
        
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, ScopeField), self.__pydantic_fields__.items()):
            scope_field: ScopeField = self.__getattribute__(field_name)
            scope_docs = scope_field.openapi_scope_descriptions()
            
            docs_dict.update(scope_docs)
            
        return docs_dict
