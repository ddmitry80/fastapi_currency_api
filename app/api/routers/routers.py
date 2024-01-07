from app.api.endpoints.auth import router as router_auth
from app.api.endpoints.exchanger import router as router_exch

all_routers = [router_auth, router_exch]
