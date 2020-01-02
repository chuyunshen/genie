from fbchat import Client, User


# TODO @chuyunshen _from_all_fetch is a private method


class CustomClient(Client):
    """CustomClient inherits from Client, to add on a method to get a list
    of Facebook/Messenger friends."""

    def get_contact_list(self):
        """Returns all contacts (friends or non-friends) of the client.
        Returns:
            list: :class:`User` objects
        Raises:
            FBchatException: If request failed
        """
        data = {"viewer": self._uid}
        j = self._payload_post("/chat/user_info_all", data)

        users = []
        for data in j.values():
            if data["type"] in ["user", "friend"]:
                users.append(User._from_all_fetch(data))
        return users
