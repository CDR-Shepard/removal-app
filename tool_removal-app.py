import streamlit as st
import pandas as pd

def remove_records_equally(df, file_name_values, other_column, other_column_values, total_to_remove):
    # Reset the DataFrame index to ensure consistency
    df = df.reset_index(drop=True)
    
    # Calculate the number of records to remove per value combination
    combinations = len(file_name_values) * len(other_column_values)
    per_combination = total_to_remove // combinations
    
    # Keep track of the total number of records removed and removal details
    total_removed = 0
    removal_details = {}  # To store how many records were removed per combination
    
    # Create a mask for rows to keep
    mask = pd.Series([True] * len(df))
    
    for file_name_val in file_name_values:
        for other_val in other_column_values:
            # Identify rows matching the current combination
            current_rows = df[(df['file name'] == file_name_val) & (df[other_column] == other_val)]
            
            # Calculate how many records to remove, considering the remaining removal quota
            remaining_to_remove = total_to_remove - total_removed
            remove_count = min(len(current_rows), per_combination, remaining_to_remove)
            
            # Update the mask to False for rows to remove
            if remove_count > 0:
                rows_to_remove = current_rows.sample(n=remove_count, random_state=1).index
                mask.iloc[rows_to_remove] = False  # Use .iloc for position-based indexing
                total_removed += remove_count
                
                # Update removal details
                removal_details[(file_name_val, other_val)] = remove_count
    
    # Check if we still need to remove more records and adjust if necessary
    if total_removed < total_to_remove:
        additional_remove_count = total_to_remove - total_removed
        additional_rows_to_remove = df[mask].sample(n=additional_remove_count, random_state=1).index
        mask.iloc[additional_rows_to_remove] = False  # Use .iloc for position-based indexing
        # Update removal details for additional removal
        removal_details['additional'] = additional_remove_count
    
    # Return the dataframe excluding the rows marked for removal and the removal details
    return df[mask], removal_details

def main():
    st.title("Data Removal Tool")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        if "file name" in df.columns:
            file_name_values = st.multiselect("Select values from 'file name'", options=df["file name"].unique())
            other_column = st.selectbox("Select another column", options=[col for col in df.columns if col != "file name"])
            
            if other_column:
                other_column_values = st.multiselect(f"Select values from '{other_column}'", options=df[other_column].unique())
                
                if other_column_values:
                    total_to_remove = st.number_input("Total amount of records to remove", min_value=0, max_value=len(df), value=0)
                    
                    if st.button("Remove Records"):
                        # Pass the entire DataFrame for processing
                        new_df, removal_details = remove_records_equally(df, file_name_values, other_column, other_column_values, total_to_remove)
                        st.write("Updated DataFrame:")
                        st.dataframe(new_df)
                        st.write("Removal Details:")
                        for key, value in removal_details.items():
                            st.write(f"{key}: {value} records removed")
                        st.download_button(label="Download updated CSV", data=new_df.to_csv(index=False).encode('utf-8'), file_name="updated.csv", mime="text/csv")
        else:
            st.error("Uploaded CSV does not contain a 'file name' column.")
            
if __name__ == "__main__":
    main()
