"""
Creación de gráficos para su uso con la librería Javascript 'ChartJS'.
"""

import random
from . import reporte


BAR = "bar"
PIE = "pie"
LINE = "line"
HORIZONTAL_BAR = "horizontalBar"


class Color():

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        self.tuple = (r, g, b)

    def __str__(self):
        return "rgb({}, {}, {})".format(self.r, self.g, self.b)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, str(self))

    def Red(self):
        return self.r

    def Green(self):
        return self.g

    def Blue(self):
        return self.b




def get_random_color():
    r = random.randint(100, 255)
    g = random.randint(100, 255)
    b = random.randint(100, 255)
    return Color(r, g, b)






class Dataset():
    """
    Represents a dataset.
    """
    def __init__(self, label="", data=[], backgroundColor="auto", **kwargs):
        self.label = label
        self.data = data

        if (backgroundColor == "auto"):
            backgroundColor = [str(get_random_color()) for i in self.data]

        self.backgroundColor = backgroundColor
        #self.kwargs = kwargs
        #self.kwargs.update({"label": self.label, "data": self.data, "backgroundColor": self.backgroundColor})

    def __str__(self):
        return self.label

    def __repr__(self):
        return "%s(%s, %s)" % (self.__class__.__name__, self.label, len(self.data))

    def __iter__(self):
        for i in range(len(self.data)):
            try:
                bgcolor = self.backgroundColor[i]
            except (IndexError):
                bgcolor = str(get_random_color())

            yield [self.data[i], bgcolor]

    def Append(self, value, bgcolor="auto"):
        self.data.append(value)
        if (bgcolor == "auto"):
            bgcolor = str(get_random_color())
        self.backgroundColor.append(bgcolor)

    def SetData(self, data, bgcolor="auto"):
        self.data = data
        if (bgcolor == "auto"):
            bgcolor = [str(get_random_color()) for i in data]
        self.backgroundColor = bgcolor

    def Json(self):
        """
        Returns a json data.
        """
        return {
            "label": self.label,
            "data": self.data,
            "backgroundColor": self.backgroundColor,
        }



class Datasets():
    """
    Represents a dataset list.
    """
    def __init__(self):
        ds = Dataset()
        self.array = [ds]

    def __iter__(self):
        for dataset in self.array:
            yield dataset

    def __getitem__(self, index):
        return self.array[index]

    def Json(self):
        """
        Returns a json datasets.
        """
        return [ds.Json() for ds in self]

    def Append(self, label="", data=[], backgroundColor=[], **kwargs):
        ds = Dataset(label=label, data=data, backgroundColor=backgroundColor, **kwargs)
        self.array.append(ds)



class Data():
    """
    Represents the chars data.
    """
    def __init__(self, labels=[], datasets=None):
        self.labels = labels
        self.datasets = datasets or Datasets()

    def Json(self):
        """
        Returns json data.
        """
        return {"labels": self.labels, "datasets": self.datasets.Json()}

    def Append(self, label="", data=[], backgroundColor=[], **kwargs):
        self.datasets.Append(label=label, data=data, backgroundColor=backgroundColor, **kwargs)

    def Update(self, dictObj, index=0):
        """
        Update from other dict object.
        """
        self.labels = list(dictObj.keys())
        self.datasets[index].SetData(list(dictObj.values()))



class BaseChart():
    """
    charts base class.
    """

    def __init__(self, chart_type=BAR, data=None, legend_display=True, title="", title_display=True, **kwargs):
        self.chart_type = chart_type or kwargs.get("type") or BAR
        self.data = data or Data()
        self.legend_display = legend_display
        self.title = title or ""
        self.title_display = title_display

        # init
        self.data.datasets[0].label = title

    def __str__(self):
        return self.title

    def Append(self, label="", data=[], backgroundColor=[], **kwargs):
        self.data.Append(label=label, data=data, backgroundColor=backgroundColor, **kwargs)

    def Json(self):
        """
        Returns a json chart content representations.
        """
        return {
            "type": self.chart_type,
            "data": self.data.Json(),
            "options": {
                "legend": {"display": self.legend_display},
                "title": {"display": self.title_display, "text": self.title},
            }
        }

    def SetDataFromDict(self, dictObj):
        """
        Set data from dict object (keys=labels, values=data).
        """
        for key in dictObj:
            self.Append(label=key, data=dictObj[key])

    def SetDataFromReporte(self, reporte):
        """
        Set data from reporte object.
        """
        totales = reporte.GetTotales()
        self.SetDataFromDict(totales)



class BarChart(BaseChart):
    """
    represents a bar graph.
    """
    chart_type = BAR

    def __init__(self, *args, **kwargs):
        BaseChart.__init__(self, chart_type=BAR, *args, **kwargs)



class LineChart(BaseChart):
    """
    Represents a line graph.
    """
    chart_type = LINE

    def __init__(self, *args, **kwargs):
        BaseChart.__init__(self, chart_type=LINE, *args, **kwargs)


class PieChart(BaseChart):
    """
    Represents a pie graph.
    """
    chart_type = PIE

    def __init__(self, *args, **kwargs):
        BaseChart.__init__(self, chart_type=PIE, *args, **kwargs)


class HorizontalBarChart(BaseChart):
    """
    Represents a horizontal bar chart.
    """
    chart_type = HORIZONTAL_BAR
    def __init__(self, *args, **kwargs):
        BaseChart.__init__(self, chart_type=HORIZONTAL_BAR, *args, **kwargs)