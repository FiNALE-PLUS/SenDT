from api.utils.auth.scopes.fields.db_access import ChartScopeField, DBReadSubScope, SongScopeField
from api.utils.auth.scopes.fields.totp_access import TOTPScopeField, TOTPVerifySubScope
from api.utils.auth.scopes.scope_manager import ScopeManager


two_factor_setup_verification_scope_manager = ScopeManager(totp_access=TOTPScopeField(user_setup_verification_access=TOTPVerifySubScope(granted=True)))

s_test = ScopeManager(
    song_access=SongScopeField(read_access=DBReadSubScope(granted=True)),
    chart_access=ChartScopeField(read_access=DBReadSubScope(granted=True))
    )