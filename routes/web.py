from masonite.routes import Route
from masonite.authentication import Auth

# Home route: authenticated users land on their home, guests go to login via middleware
ROUTES = [
    Route.get("/", "auth/HomeController@show").middleware("auth").name("auth.home")
]

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
    Route.post("/tickets/@id:int/move", "TicketController@move").middleware("auth").name("tickets.move"),
    Route.post("/tickets/@id:int/delete", "TicketController@delete").middleware("auth").name("tickets.delete"),
]

# Project routes (protected)
ROUTES += [
    Route.get("/projects", "ProjectController@index").middleware("auth").name("projects.index"),
    Route.get("/projects/create", "ProjectController@create").middleware("auth").name("projects.create"),
    Route.post("/projects", "ProjectController@store").middleware("auth").name("projects.store"),
    Route.get("/projects/@id:int", "ProjectController@show").middleware("auth").name("projects.show"),
    Route.get("/projects/@id:int/edit", "ProjectController@edit").middleware("auth").name("projects.edit"),
    Route.post("/projects/@id:int/update", "ProjectController@update").middleware("auth").name("projects.update"),
    Route.get("/projects/@id:int/board", "ProjectController@board").middleware("auth").name("projects.board"),
    Route.post("/projects/@id:int/delete", "ProjectController@delete").middleware("auth").name("projects.delete"),
]
