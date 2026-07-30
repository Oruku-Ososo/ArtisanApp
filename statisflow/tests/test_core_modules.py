"""
Comprehensive test suite for StatisFLOW AutoGLM and Chart Builder
"""

import pytest
import pandas as pd
import numpy as np
from typing import Dict, Any


class TestAutoGLM:
    """Test AutoGLM engine"""
    
    @pytest.fixture
    def count_data(self) -> pd.DataFrame:
        """Generate sample count data"""
        np.random.seed(42)
        n = 200
        
        # Simulate overdispersed count data
        treatment = np.random.choice(['A', 'B', 'C'], n)
        age = np.random.randint(18, 65, n)
        
        # Generate counts with overdispersion
        base_rate = np.where(treatment == 'A', 5, 
                            np.where(treatment == 'B', 8, 12))
        counts = np.random.negative_binomial(n=2, p=0.3, size=n) + base_rate
        
        return pd.DataFrame({
            'count': counts.astype(int),
            'treatment': treatment,
            'age': age
        })
    
    @pytest.fixture
    def binary_data(self) -> pd.DataFrame:
        """Generate sample binary outcome data"""
        np.random.seed(42)
        n = 150
        
        x1 = np.random.normal(0, 1, n)
        x2 = np.random.binomial(1, 0.5, n)
        
        # Generate probabilities
        logit_p = -1 + 0.5 * x1 + 0.8 * x2
        p = 1 / (1 + np.exp(-logit_p))
        y = np.random.binomial(1, p, n)
        
        return pd.DataFrame({
            'outcome': y,
            'predictor1': x1,
            'predictor2': x2
        })
    
    def test_poisson_model_fitting(self, count_data):
        """Test basic Poisson model fitting"""
        from statisflow.models.auto_glm import AutoGLM
        
        glm = AutoGLM(count_data)
        result = glm.fit_count_model(
            dependent='count',
            independents=['treatment', 'age'],
            family='poisson'
        )
        
        assert result.model_type == "Poisson GLM"
        assert len(result.coefficients) >= 3  # intercept + predictors
        assert result.convergence_status is True
    
    def test_automatic_negative_binomial_switch(self, count_data):
        """Test automatic switching to NB when overdispersed"""
        from statisflow.models.auto_glm import AutoGLM
        
        glm = AutoGLM(count_data)
        result = glm.fit_count_model(
            dependent='count',
            independents=['treatment', 'age'],
            family='auto'  # Should auto-detect overdispersion
        )
        
        # Should detect overdispersion and potentially switch
        assert result.overdispersion_test is not None
        assert 'conclusion' in result.overdispersion_test
    
    def test_offset_handling(self, count_data):
        """Test offset/exposure handling"""
        from statisflow.models.auto_glm import AutoGLM
        
        # Add exposure variable
        count_data['exposure'] = np.random.uniform(1, 10, len(count_data))
        
        glm = AutoGLM(count_data)
        result = glm.fit_count_model(
            dependent='count',
            independents=['treatment'],
            exposure='exposure'
        )
        
        assert result.convergence_status is True
    
    def test_logistic_regression(self, binary_data):
        """Test logistic regression"""
        from statisflow.models.auto_glm import AutoGLM
        
        glm = AutoGLM(binary_data)
        result = glm.fit_logistic_regression(
            dependent='outcome',
            independents=['predictor1', 'predictor2']
        )
        
        assert result.model_type == "Binary Logistic Regression"
        assert 'auc' in result.diagnostics
        assert 0 <= result.diagnostics['auc'] <= 1
    
    def test_separation_detection(self):
        """Test complete separation detection"""
        from statisflow.models.auto_glm import AutoGLM
        
        # Create perfectly separable data
        df = pd.DataFrame({
            'y': [0, 0, 0, 1, 1, 1],
            'x': [1, 2, 3, 4, 5, 6]  # Perfectly predicts y
        })
        
        glm = AutoGLM(df)
        result = glm._check_separation('y', ['x'])
        
        assert result['separated'] is True
        assert 'x' in result['variables']
    
    def test_multinomial_regression(self):
        """Test multinomial logistic regression"""
        from statisflow.models.auto_glm import AutoGLM
        
        np.random.seed(42)
        n = 150
        df = pd.DataFrame({
            'choice': np.random.choice(['A', 'B', 'C'], n),
            'x1': np.random.normal(0, 1, n),
            'x2': np.random.uniform(0, 1, n)
        })
        
        glm = AutoGLM(df)
        result = glm.fit_multinomial(
            dependent='choice',
            independents=['x1', 'x2']
        )
        
        assert 'Multinomial' in result.model_type


class TestChartBuilder:
    """Test Chart Builder"""
    
    @pytest.fixture
    def sample_data(self) -> pd.DataFrame:
        """Generate sample data for visualization"""
        np.random.seed(42)
        n = 100
        
        return pd.DataFrame({
            'x': np.random.uniform(0, 10, n),
            'y': np.random.uniform(0, 10, n),
            'group': np.random.choice(['A', 'B'], n),
            'size': np.random.uniform(1, 10, n),
            'category': np.random.choice(['X', 'Y', 'Z'], n)
        })
    
    def test_basic_scatter_plot(self, sample_data):
        """Test basic scatter plot creation"""
        from statisflow.visualization.chart_builder import ChartBuilder
        
        builder = ChartBuilder("scatter")
        builder.set_data(sample_data)
        builder.map_roles(x='x', y='y')
        
        spec = builder.build()
        
        assert spec['type'] == 'scatter'
        assert 'data' in spec
        assert 'encoding' in spec
        assert 'x' in spec['encoding']
        assert 'y' in spec['encoding']
    
    def test_grouped_bar_chart(self, sample_data):
        """Test grouped bar chart"""
        from statisflow.visualization.chart_builder import ChartBuilder, ScaleType
        
        # Aggregate data first
        agg_data = sample_data.groupby(['category', 'group'])['y'].mean().reset_index()
        
        builder = ChartBuilder("bar")
        builder.set_data(agg_data)
        builder.map_roles(x='category', y='y', group='group')
        builder.customize_bar(show_label=True, stack=False)
        
        spec = builder.build()
        
        assert spec['type'] == 'bar'
        assert len(spec['series']) == 2  # Two groups
    
    def test_axis_customization(self, sample_data):
        """Test axis customization"""
        from statisflow.visualization.chart_builder import ChartBuilder, ScaleType
        
        builder = ChartBuilder("scatter")
        builder.set_data(sample_data)
        builder.map_roles(x='x', y='y')
        builder.customize_axes(
            x_scale=ScaleType.LOG,
            y_min=0,
            y_max=20,
            hide_x=False
        )
        
        spec = builder.build()
        
        assert spec['xAxis']['scale'] == 'log'
        assert spec['yAxis']['min'] == 0
        assert spec['yAxis']['max'] == 20
    
    def test_violin_plot_config(self, sample_data):
        """Test violin plot configuration"""
        from statisflow.visualization.chart_builder import ChartBuilder
        
        builder = ChartBuilder("violin")
        builder.set_data(sample_data)
        builder.map_roles(x='group', y='y', color='group')
        builder.customize_violin(
            inner_box=True,
            bandwidth=0.4,
            split_by_group=False
        )
        
        spec = builder.build()
        
        assert spec['type'] == 'violin'
        assert spec.get('innerBox') is True
        assert spec.get('bandwidth') == 0.4
    
    def test_html_export(self, sample_data):
        """Test HTML export"""
        from statisflow.visualization.chart_builder import ChartBuilder
        
        builder = ChartBuilder("scatter")
        builder.set_data(sample_data)
        builder.map_roles(x='x', y='y')
        builder.set_title("Test Plot", subtitle="For testing")
        
        html = builder.render_html(width=600, height=400)
        
        assert '<html>' in html
        assert 'echarts' in html.lower()
        assert 'Test Plot' in html
        assert '600px' in html
        assert '400px' in html
    
    def test_json_export(self, sample_data):
        """Test JSON export"""
        from statisflow.visualization.chart_builder import ChartBuilder
        import json
        
        builder = ChartBuilder("scatter")
        builder.set_data(sample_data)
        builder.map_roles(x='x', y='y', color='group')
        
        json_str = builder.to_json()
        spec = json.loads(json_str)
        
        assert isinstance(spec, dict)
        assert spec['type'] == 'scatter'


class TestIntegration:
    """Integration tests combining models and visualization"""
    
    def test_model_to_visualization_pipeline(self):
        """Test full pipeline from modeling to visualization"""
        from statisflow.models.auto_glm import AutoGLM
        from statisflow.visualization.chart_builder import ChartBuilder
        
        # Generate residual plot data
        np.random.seed(42)
        n = 100
        df = pd.DataFrame({
            'y': np.random.poisson(5, n),
            'x': np.random.uniform(0, 10, n)
        })
        
        # Fit model
        glm = AutoGLM(df)
        result = glm.fit_count_model(dependent='y', independents=['x'])
        
        # Create residual plot
        residuals_df = pd.DataFrame({
            'fitted': result.predictions.values,
            'residuals': result.residuals.values
        })
        
        builder = ChartBuilder("scatter")
        builder.set_data(residuals_df)
        builder.map_roles(x='fitted', y='residuals')
        builder.set_title("Residual Plot", subtitle=f"Model: {result.model_type}")
        
        spec = builder.build()
        
        assert spec['type'] == 'scatter'
        assert 'Residual Plot' in spec['title']['text']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
