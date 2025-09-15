from masonite.routes import Route
from masonite.authentication import Auth

ROUTES = [Route.get("/", "WelcomeController@show")]

ROUTES += Auth.routes()

# Ticket routes (protected by auth via Kernel group)
ROUTES += [
    Route.get("/tickets", "TicketController@index").middleware("auth").name("tickets.index"),
    Route.get("/tickets/create", "TicketController@create").middleware("auth").name("tickets.create"),
    Route.post("/tickets", "TicketController@store").middleware("auth").name("tickets.store"),
    Route.get("/tickets/@id:int", "TicketController@show").middleware("auth").name("tickets.show"),
    Route.get("/tickets/@id:int/edit", "TicketController@edit").middleware("auth").name("tickets.edit"),
    Route.post("/tickets/@id:int/update", "TicketController@update").middleware("auth").name("tickets.update"),
    Route.post("/tickets/@id:int/comment", "TicketController@comment").middleware("auth").name("tickets.comment"),
    Route.post("/tickets/@id:int/delete", "TicketController@delete").middleware("auth").name("tickets.delete"),
]
