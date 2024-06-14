"""SalesService Test"""

from unittest.mock import patch

import pandas as pd

from app.schemas.sales_response import TotalAvgSales
from app.services.sales import SalesService


class TestSalesServiceFiltering:
    """Test filtering data"""

    def test_period_filter(
        self, testing_data: pd.DataFrame, sales_service_period: SalesService
    ):
        filtered_data = sales_service_period._filter_data(testing_data)
        assert len(filtered_data) == 3

    def test_employee_filter(
        self, testing_data: pd.DataFrame, sales_service_employee_key: SalesService
    ):
        filtered_data = sales_service_employee_key._filter_data(testing_data)
        assert len(filtered_data) == 2

    def test_product_filter(
        self, testing_data: pd.DataFrame, sales_service_product_key: SalesService
    ):
        filtered_data = sales_service_product_key._filter_data(testing_data)
        assert len(filtered_data) == 1

    def test_store_filter(
        self, testing_data: pd.DataFrame, sales_service_store_key: SalesService
    ):
        filtered_data = sales_service_store_key._filter_data(testing_data)
        assert len(filtered_data) == 2


class TestSalesServiceSalesPeriod:
    def test_employee_filter(
        self,
        testing_data: pd.DataFrame,
        sales_service_employee_key: SalesService,
        total_sales_period_employee: float,
    ):
        with patch("app.services.sales.load_data") as mock_data:
            mock_data.return_value = testing_data
            total_period_sales = sales_service_employee_key.sales_by_period()
            assert total_period_sales == total_sales_period_employee

    def test_employee_filter_empty(
        self,
        testing_data: pd.DataFrame,
        sales_service_employee_key: SalesService,
    ):
        with patch("app.services.sales.load_data") as mock_data:
            with patch(
                "app.services.sales.SalesService._filter_data"
            ) as mock_filter_data:
                mock_data.return_value = testing_data
                mock_filter_data.return_value = pd.DataFrame()
                total_period_sales = sales_service_employee_key.sales_by_period()
                assert total_period_sales == 0.0


class TestSalesServiceTotalAvg:
    def test_store_filter(
        self,
        testing_data: pd.DataFrame,
        sales_service_store_key: SalesService,
        total_avg_sales_store: TotalAvgSales,
    ):
        with patch("app.services.sales.load_data") as mock_data:
            mock_data.return_value = testing_data
            total_avg_sales = sales_service_store_key.total_avg_sales()
            assert total_avg_sales == total_avg_sales_store

    def test_store_filter_empty(
        self,
        testing_data: pd.DataFrame,
        sales_service_store_key: SalesService,
    ):
        with patch("app.services.sales.load_data") as mock_data:
            with patch(
                "app.services.sales.SalesService._filter_data"
            ) as mock_filter_data:
                mock_data.return_value = testing_data
                mock_filter_data.return_value = pd.DataFrame()
                total_avg_sales = sales_service_store_key.total_avg_sales()
                assert total_avg_sales == TotalAvgSales(total=0.0, average=0.0)
