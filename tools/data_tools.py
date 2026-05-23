import pandas as pd


class DataTools:


    # -----------------------------------
    # LOAD CSV
    # -----------------------------------

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


    # -----------------------------------
    # BASIC PROFILE
    # -----------------------------------

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


    # -----------------------------------
    # SUMMARY STATISTICS
    # -----------------------------------

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


    # -----------------------------------
    # TOP PRODUCTS ANALYSIS
    # -----------------------------------

    @staticmethod
    def top_products_analysis(df):

        possible_product_cols = [
            "product",
            "product_name",
            "category"
        ]

        possible_quantity_cols = [
            "quantity",
            "qty"
        ]

        product_col = None
        quantity_col = None


        for col in df.columns:

            if col.lower() in possible_product_cols:

                product_col = col

            if col.lower() in possible_quantity_cols:

                quantity_col = col


        if (
            product_col
            and
            quantity_col
        ):

            result = (

                df.groupby(product_col)[quantity_col]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            return result.to_dict()


        return {
            "message":
            "No suitable product columns found."
        }


    # -----------------------------------
    # MISSING VALUE ANALYSIS
    # -----------------------------------

    @staticmethod
    def missing_value_analysis(df):

        missing = (

            df.isnull()
            .sum()
            .sort_values(ascending=False)
        )

        return missing.to_dict()


    # -----------------------------------
    # CORRELATION ANALYSIS
    # -----------------------------------

    @staticmethod
    def correlation_analysis(df):

        try:

            numeric_df = (
                df.select_dtypes(
                    include=["number"]
                )
            )

            correlation = (
                numeric_df.corr()
                .round(2)
            )

            return correlation.to_dict()

        except Exception as e:

            return {
                "error": str(e)
            }


    # -----------------------------------
    # SALES TREND ANALYSIS
    # -----------------------------------

    @staticmethod
    def sales_trend_analysis(df):

        possible_date_cols = [
            "date",
            "order_date",
            "created_at"
        ]

        possible_sales_cols = [
            "sales",
            "amount",
            "revenue",
            "price"
        ]

        date_col = None
        sales_col = None


        for col in df.columns:

            if col.lower() in possible_date_cols:

                date_col = col

            if col.lower() in possible_sales_cols:

                sales_col = col


        if (
            date_col
            and
            sales_col
        ):

            try:

                df[date_col] = pd.to_datetime(
                    df[date_col]
                )

                trend = (

                    df.groupby(
                        df[date_col].dt.date
                    )[sales_col]
                    .sum()
                )

                return trend.to_dict()

            except Exception as e:

                return {
                    "error": str(e)
                }


        return {
            "message":
            "No suitable sales/date columns found."
        }