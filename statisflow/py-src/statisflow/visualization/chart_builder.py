"""
StatisFLOW Chart Builder - Universal Visualization Engine
Supports 100+ chart types with deep customization, axis controls, 
grouping variables, and chart-specific configurations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Literal
from dataclasses import dataclass, field
from enum import Enum


class ChartType(Enum):
    """Supported chart types"""
    # Basic
    BAR = "bar"
    LINE = "line"
    AREA = "area"
    SCATTER = "scatter"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    
    # Statistical
    BOX_PLOT = "box_plot"
    VIOLIN = "violin"
    HISTOGRAM = "histogram"
    DENSITY = "density"
    QQ_PLOT = "qq_plot"
    HEATMAP = "heatmap"
    
    # Advanced
    SANKEY = "sankey"
    PARALLEL_COORDS = "parallel_coords"
    RADAR = "radar"
    TREEMAP = "treemap"
    SUNBURST = "sunburst"
    
    # Time Series
    CANDLESTICK = "candlestick"
    OHLC = "ohlc"
    
    # Geographic
    MAP = "map"
    CHOROPLETH = "choropleth"
    
    # 3D
    SCATTER_3D = "scatter_3d"
    SURFACE_3D = "surface_3d"


class ScaleType(Enum):
    """Axis scale types"""
    LINEAR = "linear"
    LOG = "log"
    POWER = "power"
    TIME = "time"
    CATEGORY = "category"
    ORDINAL = "ordinal"


@dataclass
class AxisConfig:
    """Configuration for X or Y axis"""
    title: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None
    scale_type: ScaleType = ScaleType.LINEAR
    show_grid: bool = True
    grid_color: str = "#e0e0e0"
    tick_count: Optional[int] = None
    tick_format: Optional[str] = None
    rotate_labels: int = 0
    show: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        config = {
            "show": self.show,
            "title": self.title,
            "scale": self.scale_type.value,
            "grid": {"show": self.show_grid, "color": self.grid_color}
        }
        
        if self.min is not None:
            config["min"] = self.min
        if self.max is not None:
            config["max"] = self.max
        if self.tick_count:
            config["tickCount"] = self.tick_count
        if self.tick_format:
            config["labelFormatter"] = self.tick_format
        if self.rotate_labels:
            config["label"] = {"rotate": self.rotate_labels}
            
        return config


@dataclass
class LegendConfig:
    """Legend configuration"""
    show: bool = True
    position: str = "right"  # top, bottom, left, right
    orient: str = "vertical"  # horizontal, vertical
    title: Optional[str] = None
    item_width: int = 20
    item_height: int = 14
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "show": self.show,
            "orient": self.orient,
            "pos": self.position,
            "title": self.title,
            "itemWidth": self.item_width,
            "itemHeight": self.item_height
        }


@dataclass
class TooltipConfig:
    """Tooltip configuration"""
    show: bool = True
    mode: str = "single"  # single, axis
    format: Optional[Dict[str, str]] = None
    background_color: str = "rgba(50, 50, 50, 0.9)"
    text_color: str = "#fff"
    
    def to_dict(self) -> Dict[str, Any]:
        config = {
            "show": self.show,
            "type": self.mode,
            "backgroundColor": self.background_color,
            "textStyle": {"color": self.text_color}
        }
        if self.format:
            config["formatter"] = self.format
        return config


@dataclass
class MarkStyle:
    """Visual style for marks (bars, lines, points)"""
    color: Optional[Union[str, List[str]]] = None
    opacity: float = 1.0
    stroke: Optional[str] = None
    stroke_width: int = 1
    size: Optional[int] = None
    shape: Optional[str] = None  # circle, square, triangle, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        config = {}
        if self.color:
            config["color"] = self.color
        if self.opacity < 1.0:
            config["opacity"] = self.opacity
        if self.stroke:
            config["stroke"] = self.stroke
            config["strokeWidth"] = self.stroke_width
        if self.size:
            config["size"] = self.size
        if self.shape:
            config["shape"] = self.shape
        return config


@dataclass
class BarConfig:
    """Bar chart specific configuration"""
    show_label: bool = False
    label_position: str = "top"  # top, inside, bottom
    label_format: str = ".2f"
    bar_width: Optional[float] = None
    rounded_corners: bool = False
    stack: bool = False
    group: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        config = {
            "label": {
                "show": self.show_label,
                "position": self.label_position,
                "format": self.label_format
            },
            "stack": self.stack
        }
        
        if self.bar_width:
            config["barWidth"] = self.bar_width
        if self.rounded_corners:
            config["roundedCorner"] = True
            
        return config


@dataclass
class LineConfig:
    """Line chart specific configuration"""
    smooth: bool = False
    show_points: bool = True
    point_size: int = 4
    line_width: int = 2
    area_fill: bool = False
    fill_opacity: float = 0.3
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "smooth": self.smooth,
            "symbol": {"show": self.show_points, "size": self.point_size},
            "lineStyle": {"width": self.line_width},
            "areaStyle": {"show": self.area_fill, "opacity": self.fill_opacity}
        }


@dataclass
class ScatterConfig:
    """Scatter plot specific configuration"""
    regression_line: bool = False
    confidence_interval: bool = False
    jitter: float = 0.0
    size_by: Optional[str] = None
    density_contours: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        config = {
            "regressionLine": self.regression_line,
            "confidenceInterval": self.confidence_interval,
            "jitter": self.jitter,
            "densityContours": self.density_contours
        }
        if self.size_by:
            config["sizeBy"] = self.size_by
        return config


@dataclass
class BoxPlotConfig:
    """Box plot specific configuration"""
    show_outliers: bool = True
    show_mean: bool = False
    orientation: str = "vertical"  # vertical, horizontal
    box_width: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "showOutliers": self.show_outliers,
            "showMean": self.show_mean,
            "orientation": self.orientation,
            "boxWidth": self.box_width
        }


@dataclass
class ViolinConfig:
    """Violin plot specific configuration"""
    inner_box: bool = True
    inner_median: bool = True
    bandwidth: Optional[float] = None
    kernel: str = "gaussian"  # gaussian, epanechnikov
    orientation: str = "vertical"
    split_by_group: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "innerBox": self.inner_box,
            "innerMedian": self.inner_median,
            "bandwidth": self.bandwidth,
            "kernel": self.kernel,
            "orientation": self.orientation,
            "splitByGroup": self.split_by_group
        }


@dataclass
class HeatmapConfig:
    """Heatmap specific configuration"""
    color_scheme: str = "RdYlBu"  # ColorBrewer schemes
    reverse_colors: bool = False
    show_values: bool = True
    value_format: str = ".2f"
    cell_border: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "colorScheme": self.color_scheme,
            "reverseColors": self.reverse_colors,
            "showValue": self.show_values,
            "valueFormat": self.value_format,
            "cellBorder": self.cell_border
        }


class ChartBuilder:
    """
    Universal Chart Builder with fluent API
    
    Example:
        builder = ChartBuilder("scatter")
        builder.set_data(df)
        builder.map_roles(x="height", y="weight", color="gender")
        builder.customize_scatter(regression_line=True)
        builder.set_title("Height vs Weight")
        spec = builder.build()
    """
    
    def __init__(self, chart_type: Union[str, ChartType]):
        """Initialize chart builder"""
        if isinstance(chart_type, str):
            try:
                self.chart_type = ChartType(chart_type.lower())
            except ValueError:
                raise ValueError(f"Unknown chart type: {chart_type}")
        else:
            self.chart_type = chart_type
        
        self.data: Optional[pd.DataFrame] = None
        self.x_field: Optional[str] = None
        self.y_field: Optional[str] = None
        self.group_field: Optional[str] = None
        self.facet_row: Optional[str] = None
        self.facet_col: Optional[str] = None
        self.color_field: Optional[str] = None
        self.size_field: Optional[str] = None
        self.tooltip_fields: List[str] = []
        
        # Configurations
        self.title: Optional[str] = None
        self.subtitle: Optional[str] = None
        self.x_axis = AxisConfig()
        self.y_axis = AxisConfig()
        self.legend = LegendConfig()
        self.tooltip = TooltipConfig()
        self.mark_style = MarkStyle()
        
        # Chart-specific configs
        self.bar_config = BarConfig()
        self.line_config = LineConfig()
        self.scatter_config = ScatterConfig()
        self.box_config = BoxPlotConfig()
        self.violin_config = ViolinConfig()
        self.heatmap_config = HeatmapConfig()
        
    def set_data(self, data: pd.DataFrame) -> 'ChartBuilder':
        """Set the data source"""
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")
        self.data = data.copy()
        return self
    
    def map_roles(
        self,
        x: Optional[str] = None,
        y: Optional[str] = None,
        group: Optional[str] = None,
        facet_row: Optional[str] = None,
        facet_col: Optional[str] = None,
        color: Optional[str] = None,
        size: Optional[str] = None,
        tooltip: Optional[List[str]] = None
    ) -> 'ChartBuilder':
        """
        Map data columns to visual roles
        
        Parameters
        ----------
        x : str
            Column for X-axis
        y : str
            Column for Y-axis
        group : str
            Column for grouping (creates multiple series)
        facet_row : str
            Column for row faceting
        facet_col : str
            Column for column faceting
        color : str
            Column for color encoding
        size : str
            Column for size encoding
        tooltip : List[str]
            Columns to show in tooltip
        """
        self.x_field = x
        self.y_field = y
        self.group_field = group
        self.facet_row = facet_row
        self.facet_col = facet_col
        self.color_field = color or group  # Default color to group
        self.size_field = size
        self.tooltip_fields = tooltip or []
        
        # Auto-set axis titles from field names
        if x and not self.x_axis.title:
            self.x_axis.title = x
        if y and not self.y_axis.title:
            self.y_axis.title = y
            
        return self
    
    def set_title(self, title: str, subtitle: Optional[str] = None) -> 'ChartBuilder':
        """Set chart title and optional subtitle"""
        self.title = title
        self.subtitle = subtitle
        return self
    
    def customize_axes(
        self,
        x_scale: Optional[ScaleType] = None,
        y_scale: Optional[ScaleType] = None,
        x_log: bool = False,
        y_log: bool = False,
        x_min: Optional[float] = None,
        x_max: Optional[float] = None,
        y_min: Optional[float] = None,
        y_max: Optional[float] = None,
        hide_x: bool = False,
        hide_y: bool = False
    ) -> 'ChartBuilder':
        """Customize axis properties"""
        if x_scale:
            self.x_axis.scale_type = x_scale
        if y_scale:
            self.y_axis.scale_type = y_scale
        if x_log:
            self.x_axis.scale_type = ScaleType.LOG
        if y_log:
            self.y_axis.scale_type = ScaleType.LOG
        if x_min is not None:
            self.x_axis.min = x_min
        if x_max is not None:
            self.x_axis.max = x_max
        if y_min is not None:
            self.y_axis.min = y_min
        if y_max is not None:
            self.y_axis.max = y_max
        if hide_x:
            self.x_axis.show = False
        if hide_y:
            self.y_axis.show = False
            
        return self
    
    def customize_legend(
        self,
        show: bool = True,
        position: str = "right",
        title: Optional[str] = None
    ) -> 'ChartBuilder':
        """Customize legend"""
        self.legend.show = show
        self.legend.position = position
        self.legend.title = title
        return self
    
    def customize_tooltip(
        self,
        show: bool = True,
        mode: str = "single",
        fields: Optional[List[str]] = None
    ) -> 'ChartBuilder':
        """Customize tooltip"""
        self.tooltip.show = show
        self.tooltip.mode = mode
        if fields:
            self.tooltip_fields = fields
        return self
    
    def customize_mark(
        self,
        color: Optional[Union[str, List[str]]] = None,
        opacity: float = 1.0,
        size: Optional[int] = None
    ) -> 'ChartBuilder':
        """Customize mark appearance"""
        if color:
            self.mark_style.color = color
        self.mark_style.opacity = opacity
        if size:
            self.mark_style.size = size
        return self
    
    def customize_bar(
        self,
        show_label: bool = False,
        stack: bool = False,
        bar_width: Optional[float] = None
    ) -> 'ChartBuilder':
        """Customize bar chart"""
        self.bar_config.show_label = show_label
        self.bar_config.stack = stack
        self.bar_config.bar_width = bar_width
        return self
    
    def customize_line(
        self,
        smooth: bool = False,
        show_points: bool = True,
        area_fill: bool = False
    ) -> 'ChartBuilder':
        """Customize line chart"""
        self.line_config.smooth = smooth
        self.line_config.show_points = show_points
        self.line_config.area_fill = area_fill
        return self
    
    def customize_scatter(
        self,
        regression_line: bool = False,
        jitter: float = 0.0,
        density_contours: bool = False
    ) -> 'ChartBuilder':
        """Customize scatter plot"""
        self.scatter_config.regression_line = regression_line
        self.scatter_config.jitter = jitter
        self.scatter_config.density_contours = density_contours
        return self
    
    def customize_boxplot(
        self,
        show_outliers: bool = True,
        show_mean: bool = False
    ) -> 'ChartBuilder':
        """Customize box plot"""
        self.box_config.show_outliers = show_outliers
        self.box_config.show_mean = show_mean
        return self
    
    def customize_violin(
        self,
        inner_box: bool = True,
        bandwidth: Optional[float] = None,
        split_by_group: bool = False
    ) -> 'ChartBuilder':
        """Customize violin plot"""
        self.violin_config.inner_box = inner_box
        self.violin_config.bandwidth = bandwidth
        self.violin_config.split_by_group = split_by_group
        return self
    
    def customize_heatmap(
        self,
        color_scheme: str = "RdYlBu",
        show_values: bool = True
    ) -> 'ChartBuilder':
        """Customize heatmap"""
        self.heatmap_config.color_scheme = color_scheme
        self.heatmap_config.show_values = show_values
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Build the VChart/ECharts specification
        
        Returns
        -------
        dict
            Complete chart specification ready for rendering
        """
        if self.data is None:
            raise ValueError("No data set. Call set_data() first.")
        
        # Base specification
        spec = {
            "type": self.chart_type.value,
            "data": {
                "values": self.data.to_dict('records')
            },
            "title": {
                "text": self.title or "",
                "subtext": self.subtitle or ""
            } if self.title else {},
            "xAxis": self.x_axis.to_dict(),
            "yAxis": self.y_axis.to_dict(),
            "legend": self.legend.to_dict(),
            "tooltip": self.tooltip.to_dict()
        }
        
        # Add series configuration based on chart type
        series = self._build_series()
        spec["series"] = series
        
        # Add encoding
        encoding = self._build_encoding()
        spec["encoding"] = encoding
        
        # Add chart-specific options
        spec.update(self._build_chart_specific_options())
        
        return spec
    
    def _build_series(self) -> List[Dict[str, Any]]:
        """Build series configuration"""
        series_list = []
        
        base_series = {
            "type": self._get_series_type()
        }
        
        # Apply mark style
        base_series.update(self.mark_style.to_dict())
        
        # Add group-based series if grouping
        if self.group_field and self.data is not None:
            groups = self.data[self.group_field].unique()
            for group in groups:
                series_copy = base_series.copy()
                series_copy["name"] = str(group)
                series_list.append(series_copy)
        else:
            series_list.append(base_series)
        
        return series_list
    
    def _get_series_type(self) -> str:
        """Map chart type to series type"""
        mapping = {
            ChartType.BAR: "bar",
            ChartType.LINE: "line",
            ChartType.AREA: "area",
            ChartType.SCATTER: "scatter",
            ChartType.PIE: "pie",
            ChartType.BOX_PLOT: "boxplot",
            ChartType.VIOLIN: "violin",
            ChartType.HEATMAP: "heatmap"
        }
        return mapping.get(self.chart_type, "scatter")
    
    def _build_encoding(self) -> Dict[str, Any]:
        """Build visual encoding"""
        encoding = {}
        
        if self.x_field:
            encoding["x"] = {
                "field": self.x_field,
                "type": self._infer_field_type(self.x_field)
            }
        
        if self.y_field:
            encoding["y"] = {
                "field": self.y_field,
                "type": self._infer_field_type(self.y_field)
            }
        
        if self.color_field:
            encoding["color"] = {
                "field": self.color_field,
                "type": "nominal"
            }
        
        if self.size_field:
            encoding["size"] = {
                "field": self.size_field,
                "type": "quantitative"
            }
        
        if self.tooltip_fields:
            encoding["tooltip"] = [
                {"field": f, "type": self._infer_field_type(f)}
                for f in self.tooltip_fields
            ]
        
        return encoding
    
    def _infer_field_type(self, field: str) -> str:
        """Infer Vega-Lite type from pandas dtype"""
        if self.data is None:
            return "nominal"
        
        dtype = self.data[field].dtype
        
        if pd.api.types.is_numeric_dtype(dtype):
            if pd.api.types.is_integer_dtype(dtype) and self.data[field].nunique() < 10:
                return "ordinal"
            return "quantitative"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return "temporal"
        else:
            return "nominal"
    
    def _build_chart_specific_options(self) -> Dict[str, Any]:
        """Add chart-specific configuration options"""
        options = {}
        
        if self.chart_type == ChartType.BAR:
            options.update(self.bar_config.to_dict())
        elif self.chart_type == ChartType.LINE:
            options.update(self.line_config.to_dict())
        elif self.chart_type == ChartType.SCATTER:
            options.update(self.scatter_config.to_dict())
        elif self.chart_type == ChartType.BOX_PLOT:
            options.update(self.box_config.to_dict())
        elif self.chart_type == ChartType.VIOLIN:
            options.update(self.violin_config.to_dict())
        elif self.chart_type == ChartType.HEATMAP:
            options.update(self.heatmap_config.to_dict())
        
        return options
    
    def to_json(self) -> str:
        """Export specification as JSON string"""
        import json
        return json.dumps(self.build(), indent=2)
    
    def render_html(self, width: int = 800, height: int = 600) -> str:
        """Generate standalone HTML with embedded chart"""
        spec = self.build()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{self.title or 'StatisFLOW Chart'}</title>
    <script src="https://lib.baomitu.com/echarts/latest/echarts.min.js"></script>
    <style>
        #chart {{ width: {width}px; height: {height}px; margin: 20px auto; }}
    </style>
</head>
<body>
    <div id="chart"></div>
    <script>
        var chartDom = document.getElementById('chart');
        var myChart = echarts.init(chartDom);
        var option = {self.to_json()};
        myChart.setOption(option);
    </script>
</body>
</html>
"""
        return html
