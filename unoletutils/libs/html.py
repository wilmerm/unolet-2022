"""
Objetos para interpretar etiquetas HTML básicas.
"""



VALUES_HTML_FORMAT = {
    True: "true", False: "false", None: "none", 
}



class attr(object):

    def __init__(self, parent, name, value=None):

        self.__dict__["parent"] = parent
        self.__dict__["name"] = name.lower()
        self.__dict__["value"] = self.FormatValue(value=value, name=name)

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __setattr__(self, name, value):
        if name == "value":
            value = self.FormatValue(value, self.name)
        return super().__setattr__(name, value)

    def FormatValue(self, value, name=None):
        """
        Formatea el valor a uno ideal para HTML
        """
        try:
            value = VALUES_HTML_FORMAT[value]
        except (KeyError):
            value = str(value)
        if name in ("src", "class", "style"):
            value = str(value).strip()
        if name == "checked":
            value = "true"
        return value



class base(object):
    has_close_tag = True
    tag_name = ""
    # Atributos que '__setattr__' NO guardará como un objeto 'html.attr'
    no_html_attrname = ("has_close_tag", "tag_name", "parent", "inner")

    def __init__(self, parent=None, **kwargs):
        # Padre.
        self.parent = parent

        # Hijo(s)
        inner = kwargs.get("inner", [])
        if (not isinstance(inner, (list, tuple))):
            inner = [inner]
        self.inner = list(inner)

        # Asignamos los atributos.
        # El atributo class se puede asignar como: _class, css_class o cssclass
        for k, v in kwargs.items():

            # Si es un atributo no permitido., estos atributos son únicos
            # para este objeto Python.
            if (k in (self.no_html_attrname)):
                continue

            # El atributo class, al ser un nombre reservado de Python,
            # podemos asignarlo alternativamente como _class, css_class o cssclass.
            # este se agregará como '_class' y al momento de renderizar el objeto en HTML
            # se retornará el valor correcto 'class'.
            if (k == "css_class"):
                k = "_class"
            elif (k == "cssclass"):
                k = "_class"

            self.__dict__[k] = attr(self, k, v)

    def __str__(self):
        close_tagname = ""
        if self.has_close_tag:
            close_tagname = "</{tagname}>".format(tagname=self.tag_name)
        return "<{tagname}{attrs}>{children}{closetagname}".format(tagname=self.tag_name, attrs=self.GetAttrsString(), children=self.GetChildrenString(), closetagname=close_tagname)

    def __repr__(self):
        return str(self)

    def __setattr__(self, name, value):
        if name in self.no_html_attrname:
            return super().__setattr__(name, value)
        elif isinstance(value, attr):
            return super().__setattr__(name, value)
        return super().__setattr__(name, attr(self, name, value))

    def GetAttrs(self):
        """
        Obtiene un listado solo los atributos que sean instancias de 'html.attr',
        que son los atributos que serán pasados para construir el objeto HTML.
        """
        out = []
        for k, v in self.__dict__.items():
            if (not isinstance(v, attr)):
                continue
            if (k in ("_class", "cssclass", "css_class")):
                k = "class"
            out.append((k, v))
        return out

    def SetAttr(self, name, value):
        """
        Establece un atributo.
        """
        return setattr(self, name, value)

    def GetAttrsString(self):
        """
        Igual que 'self.GetAttrs' solo que este devuelve un string ideal para 
        poner en el objeto HTML.
        """
        out = " ".join(['%s="%s"' % (e[0], e[1]) for e in self.GetAttrs()])
        out = " %s" % out.strip()
        if out.replace(" ", "") == "":
            return ""
        return out

    def GetTagName(self):
        return self.__class__.__name__

    def GetChildren(self):
        """
        Obtiene el elemento hijo de este, si es que tiene.
        """
        return self.inner

    def GetChildrenString(self):
        t = ""
        for e in self.GetChildren():
            t += str(e)
        return t

    def AppendChild(self, child):
        self.inner.append(child)



class span(base):
    tag_name = "span"

    def __init__(self, parent=None, **kwargs):
        base.__init__(self, parent, **kwargs)


class a(base):
    tag_name = "a"

    def __init__(self, parent=None, **kwargs):
        base.__init__(self, parent, **kwargs)


class img(base):
    has_close_tag = False
    tag_name = "img"

    def __init__(self, parent=None, **kwargs):
        base.__init__(self, parent, **kwargs)



class label(base):
    tag_name = "label"

    def __init__(self, parent=None, **kwargs):
        base.__init__(self, parent, **kwargs)



class input(base):
    has_close_tag = False
    tag_name = "input"

    def __init__(self, parent=None, **kwargs):
        base.__init__(self, parent, **kwargs)
        _type = kwargs.get("type", "text")
        self.type = attr(self, "type", _type)



class checkbox_input(input):

    def __init__(self, parent=None, **kwargs):
        input.__init__(self, parent, **kwargs)
        self.type = attr(self, "type", "checkbox")

    def __setattr__(self, name, value):
        if name == "checked":
            if value in (None, "null", "none", False, "False", "false", 0, "0"):
                # Eliminamos este atributo.
                try:
                    self.__dict__.pop("checked")
                except (KeyError):
                    pass
                return
        return super().__setattr__(name, value)


class radio_input(input):

    def __init__(self, parent=None, **kwargs):
        input.__init__(self, parent, **kwargs)
        self.type = attr(self, "type", "radio")


class select(base):
    tag_name = "select"

    def __init__(self, parent=None, **kwargs):
        base.__init__(self, parent, **kwargs)


class option(base):
    tag_name = "option"

    def __init__(self, parent=None, **kwargs):
        base.__init__(self, parent, **kwargs)


class table(base):
    tag_name = "table"

    def __init__(self, parent=None, **kwargs):
        base.__init__(self, parent, **kwargs)

    def GetTableFromDict(self, dic):
        """
        Construye una tabla a partir de un diccionario.
        """
        table = self
        i = 0
        for key in dic:
            value = dic[key]
            row = tr(self)
            if (not isinstance(value, (list, tuple))):
                value = [value]
            ii = 0
            for v in value:
                cell = td(row)
                cell.AppendChild(key)
                row.AppendChild(cell)
                cell = td(row)
                cell.AppendChild(v)
                row.AppendChild(cell)
                ii += 1
            table.AppendChild(row)
            i += 1
        return table


class tr(base):
    tag_name = "tr"

    def __init__(self, parent=None, **kwargs):
        base.__init__(self, parent, **kwargs)

class th(base):
    tag_name = "th"

    def __init__(self, parent=None, **kwargs):
        base.__init__(self, parent, **kwargs)

class td(base):
    tag_name = "td"

    def __init__(self, parent=None, **kwargs):
        base.__init__(self, parent, **kwargs)



class ul(base):
    tag_name = "ul"

    def __init__(self, parent=None, **kwargs):
        base.__init__(self, parent, **kwargs)


class li(base):
    tag_name = "li"

    def __init__(self, parent=None, **kwargs):
        base.__init__(self, parent, **kwargs)