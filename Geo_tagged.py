import streamlit as st
from PIL import Image
import piexif
import qrcode
import io


def get_coordinates(exif_bytes):
    try:
        exif_data = piexif.load(exif_bytes)
        gps_data = exif_data.get("GPS")
        if not gps_data:
            return None

        def convert_to_degrees(value):
            d, m, s = [v[0] / v[1] for v in value]
            return d + (m / 60.0) + (s / 3600.0)

        lat = convert_to_degrees(gps_data[piexif.GPSIFD.GPSLatitude])
        if gps_data[piexif.GPSIFD.GPSLatitudeRef] == b'S':
            lat = -lat

        lon = convert_to_degrees(gps_data[piexif.GPSIFD.GPSLongitude])
        if gps_data[piexif.GPSIFD.GPSLongitudeRef] == b'W':
            lon = -lon

        return lat, lon
    except Exception as e:
        return None

def generate_google_maps_url(lat, lon):
    return f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# ---- Streamlit App ----
st.title("Geo-tagged Image Viewer")

uploaded_file = st.file_uploader("Upload a geo-tagged image", type=["jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Read EXIF bytes from the uploaded file
    uploaded_file.seek(0)
    exif_bytes = None
    try:
        img_bytes = uploaded_file.read()
        exif_bytes = piexif.load(img_bytes)
        coords = get_coordinates(img_bytes)
    except Exception:
        coords = None

    if coords:
        lat, lon = coords
        st.success(f"Coordinates extracted:\nLatitude: {lat}\nLongitude: {lon}")

        maps_url = generate_google_maps_url(lat, lon)
        st.markdown(f"[📍 View on Google Maps]({maps_url})", unsafe_allow_html=True)

        qr_buf = generate_qr_code(maps_url)
        st.image(qr_buf, caption="QR Code for Google Maps Location")
        st.download_button("Download QR Code", qr_buf, file_name="coordinates_qr.png", mime="image/png")
    else:
        st.error("No GPS data found in the image.")



