import streamlit as st
import pandas as pd

# =========================================
# 1. PAGE CONFIGURATION
# =========================================
st.set_page_config(
    page_title="Search and compare car details",
    page_icon="🚗",
    layout="wide",
)

CSV_PATH = "cars_cleaned_final.csv"

# Load only the columns used by this app to reduce memory usage.
REQUIRED_COLUMNS = [
    "id", "make", "model", "model_version", "price",
    "registration_date", "production_year", "german_hsn_tsn",
    "mileage_km", "fuel_category", "transmission", "power_hp", "power_kw",
    "body_type", "body_color", "drive_train", "cylinders", "nr_seats", "nr_doors",
    "equipment_comfort", "equipment_entertainment", "equipment_extra",
    "country_code", "seller_company_name", "seller_notes",
]


# =========================================
# 2. LOAD DATA
# =========================================
@st.cache_data(show_spinner="Loading car dataset...")
def load_data(csv_path):
    # Read the header first, then load only columns that exist in the CSV.
    available_columns = pd.read_csv(csv_path, nrows=0, encoding="utf-8-sig").columns.tolist()
    columns_to_load = [col for col in REQUIRED_COLUMNS if col in available_columns]

    df = pd.read_csv(
        csv_path,
        usecols=columns_to_load,
        low_memory=True,
        encoding="utf-8-sig",
    )

    # Remove duplicate column names if the CSV contains any.
    df = df.loc[:, ~df.columns.duplicated()].copy()

    # Ensure columns used for filters and labels exist.
    text_columns = [
        "make", "model", "model_version", "fuel_category", "body_type",
        "registration_date", "german_hsn_tsn", "transmission", "body_color",
        "drive_train", "cylinders", "equipment_comfort", "equipment_entertainment",
        "equipment_extra", "country_code", "seller_company_name", "seller_notes",
    ]
    for column in text_columns:
        if column not in df.columns:
            df[column] = "Not Available"

    # Ensure optional specifications exist even if not present in the CSV.
    for column in ["mileage_km", "production_year", "power_hp", "power_kw", "nr_seats", "nr_doors"]:
        if column not in df.columns:
            df[column] = pd.NA

    if "price" not in df.columns:
        raise ValueError("The CSV file does not contain a 'price' column.")

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"]).copy()
    df["price"] = df["price"].astype("float32")

    if "id" not in df.columns:
        df["id"] = df.index.astype(str)
    else:
        df["id"] = df["id"].astype(str)

    # Make dropdown labels unique even if duplicate IDs exist.
    df = df.drop_duplicates(subset="id", keep="first").copy()

    df["car_label"] = (
        df["make"].fillna("Unknown").astype(str)
        + " | " + df["model"].fillna("Unknown").astype(str)
        + " | " + df["model_version"].fillna("Unknown").astype(str)
        + " | €" + df["price"].map(lambda value: f"{value:,.0f}")
    )
    return df


try:
    df = load_data(CSV_PATH)
except FileNotFoundError:
    st.error(
        f"Could not find '{CSV_PATH}'. Place it in the same folder as app.py "
        "or update CSV_PATH to the correct file path."
    )
    st.stop()
except MemoryError:
    st.error(
        "Your computer ran out of memory while loading the CSV. Close other "
        "applications and try again, or reduce the columns loaded by the app."
    )
    st.stop()
except Exception as error:
    st.error(f"Could not load the car dataset: {error}")
    st.stop()

if df.empty:
    st.error("No cars with a valid price were found in the dataset.")
    st.stop()


# =========================================
# 3. DASHBOARD HEADER
# =========================================
st.title("🚗 Search and compare car details")
st.write("Find the right car for your needs and budget. Search by brand, model, budget, and fuel type.")


# =========================================
# 4. DASHBOARD SUMMARY
# =========================================
st.header("📊 Overview")
total_cars = len(df)
total_brands = df["make"].nunique()
minimum_price = int(df["price"].min())
maximum_price = int(df["price"].max())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Cars", f"{total_cars:,}")
col2.metric("Available Brands", f"{total_brands:,}")
col3.metric("Lowest Price", f"€{minimum_price:,.0f}")
col4.metric("Highest Price", f"€{maximum_price:,.0f}")


# =========================================
# 5. AVAILABLE BRANDS
# =========================================
st.subheader("🚘 Available Car Brands in Europe")
brands = sorted(df["make"].dropna().astype(str).unique().tolist())
st.write(" | ".join(brands))


# =========================================
# 6. FIND YOUR CAR
# =========================================
st.divider()
st.header("🔎 Find Your Car")
st.write("Enter your car search details below.")

col1, col2 = st.columns(2)
available_brands = sorted(df["make"].dropna().astype(str).unique().tolist())
with col1:
    selected_brand = st.selectbox("Choose Brand", options=["All Brands"] + available_brands)

with col2:
    if selected_brand == "All Brands":
        available_models = sorted(df["model"].dropna().astype(str).unique().tolist())
    else:
        available_models = sorted(
            df.loc[df["make"] == selected_brand, "model"].dropna().astype(str).unique().tolist()
        )
    selected_model = st.selectbox("Choose Model", options=["All Models"] + available_models)

col3, col4 = st.columns(2)
with col3:
    fuel_options = sorted(df["fuel_category"].dropna().astype(str).unique().tolist())
    selected_fuel = st.selectbox("Fuel Type", options=["All Fuel Types"] + fuel_options)

with col4:
    budget_step = 1000 if maximum_price - minimum_price >= 1000 else 1
    price_range = st.slider(
        "💰 Select Your Budget Range (€)",
        min_value=minimum_price,
        max_value=maximum_price,
        value=(minimum_price, maximum_price),
        step=budget_step,
        format="€%d",
    )

search_clicked = st.button("🔍 Search Cars", type="primary", use_container_width=True)


# =========================================
# 7. SEARCH RESULTS
# =========================================
if search_clicked:
    filtered = df

    if selected_brand != "All Brands":
        filtered = filtered[filtered["make"] == selected_brand]
    if selected_model != "All Models":
        filtered = filtered[filtered["model"] == selected_model]
    if selected_fuel != "All Fuel Types":
        filtered = filtered[filtered["fuel_category"] == selected_fuel]

    filtered = filtered[filtered["price"].between(price_range[0], price_range[1])].copy()
    filtered = filtered.drop_duplicates(subset="id")

    st.session_state["search_results"] = filtered["id"].tolist()
    st.session_state["search_performed"] = True
    st.session_state.pop("first_car", None)
    st.session_state.pop("second_car", None)


# All results and comparison UI are inside this guard so `results` is always defined.
if st.session_state.get("search_performed", False):
    result_ids = st.session_state.get("search_results", [])
    results = df[df["id"].isin(result_ids)].drop_duplicates(subset="id").copy()

    st.divider()
    st.header("🚘 Matching Cars")
    st.write(f"Found **{len(results):,} matching cars**.")

    if results.empty:
        st.warning("No cars match your selections. Try changing the brand, model, fuel type, or budget.")
    else:
        display_columns = [
            "make", "model", "model_version", "price", "registration_date",
            "german_hsn_tsn", "mileage_km", "fuel_category", "transmission",
            "power_hp", "body_type", "body_color", "drive_train", "cylinders",
            "equipment_comfort", "equipment_entertainment", "equipment_extra",
            "country_code", "seller_company_name", "seller_notes",
        ]
        display_columns = list(dict.fromkeys(col for col in display_columns if col in results.columns))

        st.dataframe(results[display_columns], use_container_width=True, hide_index=True)

        # General notice if any matching car has missing seller information.
        seller_text = results["seller_company_name"].fillna("").astype(str).str.strip().str.lower()
        missing_seller_mask = seller_text.isin(["", "not available", "nan", "none", "null"])
        if missing_seller_mask.any():
            st.info(
                "Some matching cars have no seller information in our dataset. You can still compare "
                "their prices and specifications. Please check the original listing on the company's "
                "website if a listing link is available."
            )
# =========================================
# 8. FIND MATCHING CARS FOR BOTH SELECTIONS
# =========================================
st.divider()
st.header("⚖️ Compare Two Cars")

st.write("Enter your preferences for each car, then select the exact cars to compare.")

# Get available options
available_brands = sorted(df["make"].dropna().astype(str).unique())
available_fuels = sorted(df["fuel_category"].dropna().astype(str).unique())

min_price = int(df["price"].min())
max_price = int(df["price"].max())
price_step = 1000 if max_price - min_price >= 1000 else 1


# =========================================
# HELPER FUNCTION
# =========================================
def get_matching_cars(data, brand, model, fuel, budget):
    filtered = data.copy()

    if brand != "All Brands":
        filtered = filtered[filtered["make"] == brand]

    if model != "All Models":
        filtered = filtered[filtered["model"] == model]

    if fuel != "All Fuel Types":
        filtered = filtered[filtered["fuel_category"] == fuel]

    filtered = filtered[
        filtered["price"].between(budget[0], budget[1])
    ]

    return filtered.drop_duplicates(subset="id").copy()


# =========================================
# 9. CAR 1 AND CAR 2 INPUTS
# =========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚘 Car 1")

    make1 = st.selectbox(
        "Brand — Car 1",
        ["All Brands"] + available_brands,
        key="compare_make1"
    )

    models1 = sorted(
        df.loc[df["make"] == make1, "model"].dropna().astype(str).unique()
    ) if make1 != "All Brands" else sorted(
        df["model"].dropna().astype(str).unique()
    )

    model1 = st.selectbox(
        "Model — Car 1",
        ["All Models"] + models1,
        key="compare_model1"
    )

    fuel1 = st.selectbox(
        "Fuel Type — Car 1",
        ["All Fuel Types"] + available_fuels,
        key="compare_fuel1"
    )

    budget1 = st.slider(
        "Price Range — Car 1 (€)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=price_step,
        key="compare_budget1"
    )

with col2:
    st.subheader("🚗 Car 2")

    make2 = st.selectbox(
        "Brand — Car 2",
        ["All Brands"] + available_brands,
        key="compare_make2"
    )

    models2 = sorted(
        df.loc[df["make"] == make2, "model"].dropna().astype(str).unique()
    ) if make2 != "All Brands" else sorted(
        df["model"].dropna().astype(str).unique()
    )

    model2 = st.selectbox(
        "Model — Car 2",
        ["All Models"] + models2,
        key="compare_model2"
    )

    fuel2 = st.selectbox(
        "Fuel Type — Car 2",
        ["All Fuel Types"] + available_fuels,
        key="compare_fuel2"
    )

    budget2 = st.slider(
        "Price Range — Car 2 (€)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=price_step,
        key="compare_budget2"
    )


# =========================================
# 10. FIND MATCHES BUTTON
# =========================================
if st.button("🔍 Find Matching Cars", key="find_comparison_cars"):

    matches1 = get_matching_cars(df, make1, model1, fuel1, budget1)
    matches2 = get_matching_cars(df, make2, model2, fuel2, budget2)

    # Store IDs rather than entire DataFrames in session state
    st.session_state["compare_ids1"] = matches1["id"].tolist()
    st.session_state["compare_ids2"] = matches2["id"].tolist()

    # Reset previous selections
    st.session_state.pop("exact_car1", None)
    st.session_state.pop("exact_car2", None)
    st.session_state.pop("comparison_confirmed", None)


# =========================================
# 11. SELECT ONE EXACT CAR FROM EACH LIST
# =========================================
if (
    "compare_ids1" in st.session_state
    and "compare_ids2" in st.session_state
):
    ids1 = st.session_state["compare_ids1"]
    ids2 = st.session_state["compare_ids2"]

    matches1 = df[df["id"].isin(ids1)].drop_duplicates(subset="id")
    matches2 = df[df["id"].isin(ids2)].drop_duplicates(subset="id")

    st.subheader("Choose the Exact Cars")

    select_col1, select_col2 = st.columns(2)

    with select_col1:
        st.write(f"Car 1: **{len(matches1):,} matching cars**")

        if not matches1.empty:
            lookup1 = matches1.set_index("id", drop=False)

            selected_id1 = st.selectbox(
                "Select one exact Car 1",
                options=lookup1.index.tolist(),
                format_func=lambda x: lookup1.loc[x, "car_label"],
                key="exact_car1"
            )

    with select_col2:
        st.write(f"Car 2: **{len(matches2):,} matching cars**")

        if not matches2.empty:
            lookup2 = matches2.set_index("id", drop=False)

            selected_id2 = st.selectbox(
                "Select one exact Car 2",
                options=lookup2.index.tolist(),
                format_func=lambda x: lookup2.loc[x, "car_label"],
                key="exact_car2"
            )

    if matches1.empty:
        st.warning("No cars match Car 1's preferences. Change the filters and try again.")

    if matches2.empty:
        st.warning("No cars match Car 2's preferences. Change the filters and try again.")

    # =========================================
    # 12. CONFIRM THE COMPARISON
    # =========================================
    if not matches1.empty and not matches2.empty:

        if st.button("⚖️ Compare Selected Cars", type="primary"):

            st.session_state["comparison_confirmed"] = True

        if st.session_state.get("comparison_confirmed", False):

            car1 = lookup1.loc[st.session_state["exact_car1"]]
            car2 = lookup2.loc[st.session_state["exact_car2"]]

            # =========================================
            # 13. SELLER INFORMATION
            # =========================================
            st.subheader("🏢 Seller Information")

            def show_seller_notice(car, label):
                seller = car.get("seller_company_name", pd.NA)

                if (
                    pd.isna(seller)
                    or str(seller).strip().lower()
                    in {"", "not available", "nan", "none", "null"}
                ):
                    st.warning(
                        f"{label}: Seller information is not available in our dataset. "
                        "You can still compare this car's price and specifications "
                        "with the other car. Please check the original listing on "
                        "the company's website if a listing link is available."
                    )
                else:
                    st.info(f"{label} seller: {seller}")

            seller_col1, seller_col2 = st.columns(2)

            with seller_col1:
                show_seller_notice(car1, "Car 1")

            with seller_col2:
                show_seller_notice(car2, "Car 2")

            # =========================================
            # 14. PRICE COMPARISON
            # =========================================
            st.subheader("🏆 Price Comparison")

            price1 = float(car1["price"])
            price2 = float(car2["price"])

            price_col1, price_col2 = st.columns(2)

            with price_col1:
                st.markdown(f"### 🚘 {car1['make']} {car1['model']}")
                st.metric("Car 1 Price", f"€{price1:,.0f}")

            with price_col2:
                st.markdown(f"### 🚗 {car2['make']} {car2['model']}")
                st.metric("Car 2 Price", f"€{price2:,.0f}")

            difference = abs(price1 - price2)

            if price1 < price2:
                st.success(f"Car 1 is cheaper by €{difference:,.0f}.")
            elif price2 < price1:
                st.success(f"Car 2 is cheaper by €{difference:,.0f}.")
            else:
                st.info("Both cars have the same listed price.")

            # =========================================
            # 15. SIDE-BY-SIDE SPECIFICATIONS
            # =========================================
            st.subheader("📋 Side-by-Side Specifications")

            comparison_fields = {
                "Brand": "make",
                "Model": "model",
                "Version": "model_version",
                "Price (€)": "price",
                "Registration Date": "registration_date",
                "Production Year": "production_year",
                "Mileage (km)": "mileage_km",
                "Fuel Type": "fuel_category",
                "Transmission": "transmission",
                "Power (HP)": "power_hp",
                "Power (kW)": "power_kw",
                "Body Type": "body_type",
                "Body Color": "body_color",
                "Seats": "nr_seats",
                "Doors": "nr_doors",
                "Drive Train": "drive_train",
                "Cylinders": "cylinders"
            }

            comparison_rows = []

            for label, column in comparison_fields.items():
                value1 = car1.get(column, "Not Available")
                value2 = car2.get(column, "Not Available")

                if column == "price":
                    value1 = f"€{price1:,.0f}"
                    value2 = f"€{price2:,.0f}"
                else:
                    if pd.isna(value1) or str(value1).strip() == "":
                        value1 = "Not Available"

                    if pd.isna(value2) or str(value2).strip() == "":
                        value2 = "Not Available"

                comparison_rows.append({
                    "Specification": label,
                    "Car 1": value1,
                    "Car 2": value2
                })

            st.dataframe(
                pd.DataFrame(comparison_rows),
                use_container_width=True,
                hide_index=True
            )