import streamlit as st
import numpy as np

# Set the title and description of the app
st.title("Trigonometric App")
st.write("This app solves complex trigonometric problems!")

# Function to solve the problem
def solve_problem(angle):
    radians = np.radians(angle)
    sine = np.sin(radians)
    cosine = np.cos(radians)
    tangent = np.tan(radians)

    return sine, cosine, tangent

# Input angle from the user
angle_input = st.number_input("Enter an angle (in degrees): ")

# Solve the problem and display the results
if st.button("Solve"):
    sine, cosine, tangent = solve_problem(angle_input)
    st.write(f"Sine: {sine}")
    st.write(f"Cosine: {cosine}")
    st.write(f"Tangent: {tangent}")