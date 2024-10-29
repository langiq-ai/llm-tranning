import streamlit as st

# Initialize session state to store products if not already initialized
if 'products' not in st.session_state:
    st.session_state['products'] = []

# Display the list of products
st.header("Product List")
for product in st.session_state['products']:
    st.subheader(product['title'])
    st.write(product['description'])

# Form to add a new product
st.header("Add a New Product")
with st.form(key='product_form'):
    product_title = st.text_input("Product Title")
    product_description = st.text_area("Product Description", height=100)
    submit_button = st.form_submit_button(label='Add Product')

    if submit_button:
        # Append the new product to the top of the list
        st.session_state['products'].insert(0, {
            'title': product_title,
            'description': product_description
        })
        st.rerun()

