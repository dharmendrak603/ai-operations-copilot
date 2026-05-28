import pandas as pd


class DataTools:

    @staticmethod
    def load_csv(uploaded_file):

        try:

            df = pd.read_csv(uploaded_file)

            return {
                "status": "success",
                "dataframe": df
            }

        except Exception as e:

            return {
                "status": "error",
                "message": str(e)
            }

    @staticmethod
    def get_basic_profile(df):

        profile = {

            "rows": df.shape[0],

            "columns": df.shape[1],

            "column_names": list(df.columns),

            "missing_values": (
                df.isnull().sum().to_dict()
            ),

            "data_types": (
                df.dtypes.astype(str).to_dict()
            )
        }

        return profile

    @staticmethod
    def get_summary_statistics(df):

        try:

            summary = (
                df.describe(include="all")
                .fillna("")
                .to_string()
            )

            return summary

        except Exception as e:

            return str(e)

    # =========================================================
    # NEW KPI ENGINE
    # =========================================================

    @staticmethod
    def find_matching_column(df, possible_names):

        normalized_columns = {
            col.lower().replace(" ", "").replace("_", ""): col
            for col in df.columns
        }

        for name in possible_names:

            normalized_name = (
                name.lower()
                .replace(" ", "")
                .replace("_", "")
            )

            if normalized_name in normalized_columns:
                return normalized_columns[normalized_name]

        return None

    @staticmethod
    def clean_numeric_column(df, column_name):

        try:

            return (
                df[column_name]
                .astype(str)
                .replace(r'[\$,]', '', regex=True)
                .astype(float)
            )

        except Exception:
            return pd.Series([0] * len(df))

    @staticmethod
    def calculate_kpis(df):

        kpis = {}

        try:

            # =====================================================
            # DETECT IMPORTANT COLUMNS
            # =====================================================

            total_price_col = DataTools.find_matching_column(
                df,
                [
                    "totalprice",
                    "total_price",
                    "amount",
                    "revenue",
                    "sales"
                ]
            )

            quantity_col = DataTools.find_matching_column(
                df,
                [
                    "quantity",
                    "qty",
                    "units"
                ]
            )

            product_col = DataTools.find_matching_column(
                df,
                [
                    "product",
                    "productname",
                    "item"
                ]
            )

            payment_status_col = DataTools.find_matching_column(
                df,
                [
                    "paymentstatus",
                    "status",
                    "payment_status"
                ]
            )

            customer_col = DataTools.find_matching_column(
                df,
                [
                    "customerid",
                    "customer_id",
                    "customer"
                ]
            )

            # =====================================================
            # TOTAL ORDERS
            # =====================================================

            kpis["total_orders"] = len(df)

            # =====================================================
            # TOTAL REVENUE
            # =====================================================

            total_revenue = 0

            if total_price_col:

                revenue_series = DataTools.clean_numeric_column(
                    df,
                    total_price_col
                )

                total_revenue = revenue_series.sum()

            kpis["total_revenue"] = round(total_revenue, 2)

            # =====================================================
            # AVG ORDER VALUE
            # =====================================================

            if len(df) > 0:

                avg_order_value = (
                    total_revenue / len(df)
                )

            else:
                avg_order_value = 0

            kpis["avg_order_value"] = round(
                avg_order_value,
                2
            )

            # =====================================================
            # TOTAL QUANTITY
            # =====================================================

            total_quantity = 0

            if quantity_col:

                quantity_series = DataTools.clean_numeric_column(
                    df,
                    quantity_col
                )

                total_quantity = quantity_series.sum()

            kpis["total_quantity"] = round(
                total_quantity,
                2
            )

            # =====================================================
            # UNIQUE CUSTOMERS
            # =====================================================

            if customer_col:

                kpis["unique_customers"] = (
                    df[customer_col]
                    .nunique()
                )

            else:

                kpis["unique_customers"] = "N/A"

            # =====================================================
            # PAYMENT COMPLETION RATE
            # =====================================================

            if payment_status_col:

                paid_count = (
                    df[payment_status_col]
                    .astype(str)
                    .str.lower()
                    .str.contains("paid")
                    .sum()
                )

                payment_completion_rate = (
                    paid_count / len(df)
                ) * 100

                kpis["payment_completion_rate"] = (
                    round(payment_completion_rate, 2)
                )

            else:

                kpis["payment_completion_rate"] = "N/A"

            # =====================================================
            # TOP PRODUCT
            # =====================================================

            if product_col and total_price_col:

                temp_df = df.copy()

                temp_df["__revenue__"] = (
                    DataTools.clean_numeric_column(
                        temp_df,
                        total_price_col
                    )
                )

                grouped = (
                    temp_df
                    .groupby(product_col)["__revenue__"]
                    .sum()
                    .sort_values(ascending=False)
                )

                if len(grouped) > 0:

                    kpis["top_product"] = grouped.index[0]

                    kpis["top_product_revenue"] = round(
                        grouped.iloc[0],
                        2
                    )

                else:

                    kpis["top_product"] = "N/A"
                    kpis["top_product_revenue"] = 0

            else:

                kpis["top_product"] = "N/A"
                kpis["top_product_revenue"] = 0

            return {
                "status": "success",
                "kpis": kpis
            }

        except Exception as e:

            return {
                "status": "error",
                "message": str(e)
            }