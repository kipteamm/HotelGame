import ujson


class MapData:
    def __init__(self, data_file: str):
        self.data: dict

        with open(data_file, "r") as file:
            self.data = ujson.load(file)

        self.tiles: dict = self.data["tiles"]

    def get_tile(self, tile_id: int) -> dict[str, int]:
        return self.tiles.get(f"tile_{tile_id}", {"x": 500, "y": 500})

    @property
    def starting_positions(self) -> dict[str, dict[str, int]]:
        return self.data["starting_positions"]
