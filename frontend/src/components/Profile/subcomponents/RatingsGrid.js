import React from 'react';

export function RatingsGrid({ ratings, overall }) {
    return (
        <section className='profile-section'>
            <h2>Elo Ratings</h2>
            <div className='overall-rating'>
                <span className='label'>Overall Ranking:</span>
                <span className='value'>{Math.round(overall)}</span>
            </div>
            <div className='ratings-grid'>
                {ratings.length > 0 ? ratings.map(r => (
                    <div key={r.variant} className='rating-item'>
                        <span className='variant-name'>{r.variant.charAt(0).toUpperCase() + r.variant.slice(1)}</span>
                        <span className='variant-rating'>{Math.round(r.rating)}</span>
                        <span className='variant-rd'>±{Math.round(r.rd)}</span>
                    </div>
                )) : <p>No games played yet.</p>}
            </div>
        </section>
    );
}
