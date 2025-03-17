import ujson


class MapData:
    def __init__(self, data_file: str):
        self.data: dict

        with open(data_file, "r") as file:
            self.data = ujson.load(file)

    @property
    def starting_positions(self) -> dict[str, dict[str, int]]:
        return self.data["starting_positions"]
