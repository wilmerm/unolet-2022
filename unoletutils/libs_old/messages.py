"""
Genera mensajes en clases que pueden ser utilizados por otras instancias.
"""


class Message(object):
    """
    Representa un único mensaje.
    """
    def __init__(self, title, message):
        ...


class Messages(object):
    """
    Guarda mensajes en sus atributos de clases que pueden ser facilmente
    compartidos en la instancia actual en ejecución del Sistema.
    
    """
    _dict = {}

    def __str__(self):
        return ". ".join([f"{k}: {v}" for k, v in self])

    def __repr__(self):
        return f"Message({repr(Message._dict)})"

    def __iter__(self):
        for key, value in Message._dict.items():
            yield (key, value)

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    @classmethod
    def clear(self, key=None):
        """
        Elimina toda la pila de mensajes, o solo el que se indique en 'key'.
        """
        if key != None:
            return Message._dict.pop(key)
        Message._dict.clear()

    @classmethod
    def pop(self, key):
        """
        Elimina y retorna el mensaje con la clave indicada.
        """
        return Message._dict.pop(key)

    @classmethod
    def get(self, key):
        """
        Obtiene el mensaje con la clave indicada.
        """
        return Message._dict.get(key)

    

raise NotImplementedError("En fase de desarrollo.")