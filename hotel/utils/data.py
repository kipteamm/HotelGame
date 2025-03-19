import random
import ujson


class MapData:
    def __init__(self, data_file: str):
        self.data: dict

        with open(data_file, "r") as file:
            self.data = ujson.load(file)

        self.tiles: dict = self.data["tiles"]
        self.hotels: dict = self.data["hotels"]
        self.actions: dict = self.data["actions"]

    def get_tile_data(self, tile_id: int) -> dict:
        return self.tiles.get(f"tile_{tile_id}", {"x": 500, "y": 500})
    
    def get_tile(self, road_configuration: str, start_tile_id: int, moves: int) -> tuple[dict[str, int | str], int]:
        tiles: list = self.data["road_configurations"][road_configuration]
        current_tile_index = tiles.index(start_tile_id)
        next_tile_id = tiles[(current_tile_index + moves) % len(tiles)]

        return self.get_tile_data(next_tile_id), next_tile_id
    
    def get_moves(self, road_configuration: str, start_tile_id: int, moves: int) -> list[dict[str, int]]:
        tiles: list = self.data["road_configurations"][road_configuration]
        current_tile_index = tiles.index(start_tile_id)
        _moves = []

        for i in range(moves + 1):
            _moves.append({"x": self.tiles[f"tile_{tiles[(current_tile_index + i) % len(tiles)]}"]["x"], "y": self.tiles[f"tile_{tiles[(current_tile_index + i) % len(tiles)]}"]["y"]})

        return _moves
    
    def get_hotel(self, hotel: str) -> dict | None:
        return self.hotels.get(hotel, None)
    
    def get_random_action(self) -> str:
        keys = list(self.actions.keys())
        weights = [int(k) for k in keys]
        return self.actions[random.choices(keys, weights=weights)[0]]

    @property
    def starting_positions(self) -> dict[str, dict[str, int]]:
        return self.data["starting_positions"]
