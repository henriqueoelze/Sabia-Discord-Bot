class Proxy(object):
    def __init__(
            self,
            announce_channel_id=None,
            rules={},
    ):
        self.announce_channel_id: int = announce_channel_id
        self.rules: dict = rules

    def set_announce_channel(self, channel_id: int):
        self.announce_channel_id = channel_id

    def get_announce_channel(self) -> int:
        return self.announce_channel_id

    def add_rule(self, filter: str, target: int):
        self.rules[filter] = target

    def remove_rule(self, filter):
        self.rules.pop(filter, None)

    def get_forward_channel(self, filter: str) -> int:
        return self.rules[filter]

    def clear(self):
        self.rules = {}
