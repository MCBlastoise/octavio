'use client';

import { useState } from 'react';
import { Marker, Popup } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

export default function MarkerPopup({ instrument }) {
    const [popupVisible, setPopupVisible] = useState(false);

    return (
        <>
            <Marker
                longitude={instrument.longitude}
                latitude={instrument.latitude}
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
                popupVisible &&
                <Popup
                    longitude={instrument.longitude}
                    latitude={instrument.latitude}
                    closeButton={false}
                    anchor="bottom-left"
                    offset={15}
                >
                    {instrument.label}
                </Popup>
            }
        </>
    )
}
