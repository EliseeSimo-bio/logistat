import pandas as pd
import pytest

from logistat.config import FICHIER_ECHANTILLON
from logistat.donnees import lire_commandes_csv


@pytest.fixture(scope="session")
def commandes() -> pd.DataFrame:
    """Échantillon versionné de 3 000 commandes réelles (disponible en CI)."""
    return lire_commandes_csv(FICHIER_ECHANTILLON)


def brut_minimal() -> pd.DataFrame:
    """Trois articles, deux commandes, au format exact du CSV DataCo."""
    base = {
        "Type": "DEBIT",
        "Days for shipping (real)": 5,
        "Days for shipment (scheduled)": 4,
        "Benefit per order": 10.0,
        "Sales per customer": 90.0,
        "Delivery Status": "Late delivery",
        "Late_delivery_risk": 1,
        "Category Id": 1,
        "Category Name": "Cleats",
        "Customer City": "Caguas",
        "Customer Country": "Puerto Rico",
        "Customer Email": "XXXXXXXXX",
        "Customer Fname": "Ana",
        "Customer Id": 7,
        "Customer Lname": "Diaz",
        "Customer Password": "XXXXXXXXX",
        "Customer Segment": "Consumer",
        "Customer State": "PR",
        "Customer Street": "1 Calle",
        "Customer Zipcode": 725.0,
        "Department Id": 2,
        "Department Name": "Apparel",
        "Latitude": 18.2,
        "Longitude": -66.0,
        "Market": "LATAM",
        "Order City": "Lima",
        "Order Country": "Perú",
        "Order Customer Id": 7,
        "order date (DateOrders)": "1/31/2018 22:56",
        "Order Id": 100,
        "Order Item Cardprod Id": 365,
        "Order Item Discount": 10.0,
        "Order Item Discount Rate": 0.1,
        "Order Item Id": 1,
        "Order Item Product Price": 50.0,
        "Order Item Profit Ratio": 0.11,
        "Order Item Quantity": 2,
        "Sales": 100.0,
        "Order Item Total": 90.0,
        "Order Profit Per Order": 10.0,
        "Order Region": "South America",
        "Order State": "Lima",
        "Order Status": "COMPLETE",
        "Order Zipcode": None,
        "Product Card Id": 365,
        "Product Category Id": 1,
        "Product Description": None,
        "Product Image": "http://images.acmesports.sports/x",
        "Product Name": "Cleats X",
        "Product Price": 50.0,
        "Product Status": 0,
        "shipping date (DateOrders)": "2/5/2018 22:56",
        "Shipping Mode": "Standard Class",
    }
    l2 = {
        **base,
        "Order Item Id": 2,
        "Category Name": "Golf Balls",
        "Department Name": "Golf",
        "Product Card Id": 400,
        "Order Item Product Price": 200.0,
        "Order Item Quantity": 1,
        "Sales": 200.0,
        "Order Item Discount": 0.0,
        "Order Item Total": 200.0,
        "Order Profit Per Order": 50.0,
    }
    l3 = {
        **base,
        "Order Id": 101,
        "Order Item Id": 3,
        "order date (DateOrders)": "1/2/2015 08:00",
        "shipping date (DateOrders)": "1/2/2015 08:00",
        "Days for shipping (real)": 0,
        "Days for shipment (scheduled)": 0,
        "Shipping Mode": "Same Day",
        "Delivery Status": "Shipping canceled",
        "Order Status": "CANCELED",
        "Late_delivery_risk": 0,
    }
    return pd.DataFrame([base, l2, l3])
