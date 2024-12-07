class Proxy(object):
    def __init__(
            self,
            announce_channel_id=None,
            rules={},
    ):
        self.announce_channel_id: int = announce_channel_id
        self.rules: dict[int, int] = rules

    def has_rule(self, webhook_id: int) -> bool:
        return str(webhook_id) in self.rules

    def set_announce_channel(self, channel_id: int):
        self.announce_channel_id = channel_id

    def get_announce_channel(self) -> int:
        return self.announce_channel_id

    def add_rule(self, webhook_id: int, target: int):
        self.rules[webhook_id] = target

    def remove_rule(self, webhook_id: int):
        self.rules.pop(webhook_id, None)

    def get_all(self) -> dict[int, int]:
        return self.rules

    def get_destination(self, webhook_id: int) -> int:
        return self.rules[webhook_id]

    def clear(self):
        self.rules = {}
