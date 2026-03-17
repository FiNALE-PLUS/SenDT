from api.utils.auth.scopes.fields.db_access import ChartScopeField, DBReadSubScope, SongScopeField
from api.utils.auth.scopes.fields.totp_access import TOTPScopeField, TOTPTokenSubScope, TOTPVerifySubScope
from api.utils.auth.scopes.scope_manager import ScopeManager


two_factor_setup_verification_scope_manager = ScopeManager(totp_access=TOTPScopeField(user_setup_verification_access=TOTPVerifySubScope(granted=True)))
two_factor_access_request_token_scope_manager = ScopeManager(totp_access=TOTPScopeField(authenticate_access_token_access=TOTPTokenSubScope(granted=True)))

s_test = ScopeManager(
    song_access=SongScopeField(read_access=DBReadSubScope(granted=True)),
    chart_access=ChartScopeField(read_access=DBReadSubScope(granted=True))
    )