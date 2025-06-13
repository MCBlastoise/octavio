'use client';

import { useState } from 'react';
import { Marker, Popup } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

export default function MarkerPopup({ latitude, longitude }) {
    const [popupVisible, setPopupVisible] = useState(false);

    return (
        <>
            <Marker
                longitude={longitude}
                latitude={latitude}
            >
                <div
                    style={{ color: 'red', fontSize: '24px' }}
                    onMouseEnter={ () => {setPopupVisible(true)} }
                    onMouseLeave={ () => {setPopupVisible(false)} }
                >
                    📍
                </div>
            </Marker>
            {
                false &&
                <Popup
                    longitude={longitude}
                    latitude={latitude}
                    closeButton={false}
                    anchor="bottom-left"
                    offset={15}
                />
            }
        </>
    )
}
