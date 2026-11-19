import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';

const Home = () => {
    const [stats, setStats] = useState(null);
    const [health, setHealth] = useState(null);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [statsData, healthData] = await Promise.all([
                api.getStats(),
                api.healthCheck()
            ]);
            setStats(statsData);
            setHealth(healthData);
        } catch (error) {
            console.error('Failed to fetch data:', error);
        }
    };

    return (
        <div className="container" style={{ padding: '2rem 1rem' }}>
            {/* Hero Section */}
            <div className="text-center mb-2">
                <h1 style={{
                    fontSize: '3.5rem',
                    background: 'var(--gradient-primary)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    marginBottom: '1rem'
                }}>
                    👋 PrivacyFace
                </h1>
                <p style={{ fontSize: '1.25rem', color: 'var(--color-text-secondary)', maxWidth: '600px', margin: '0 auto' }}>
                    Consent-based, lightweight face matching demo
                </p>
                <p style={{ color: 'var(--color-text-muted)', marginTop: '0.5rem' }}>
                    OpenCV Haar detection • Spatial LBP matching • Encrypted descriptors
                </p>
            </div>

            {/* Status Card */}
            {health && (
                <div className="glass-card mb-2">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', justifyContent: 'center' }}>
                        <div style={{
                            width: '12px',
                            height: '12px',
                            borderRadius: '50%',
                            background: health.status === 'healthy' ? 'var(--color-success)' : 'var(--color-danger)',
                            boxShadow: `0 0 10px ${health.status === 'healthy' ? 'var(--color-success)' : 'var(--color-danger)'}`
                        }}></div>
                        <span style={{ fontWeight: 500 }}>
                            System Status: {health.status === 'healthy' ? '✅ Healthy' : '❌ Unhealthy'}
                        </span>
                    </div>
                </div>
            )}

            {/* Stats */}
            {stats && (
                <div className="grid grid-2 mb-2">
                    <div className="glass-card text-center">
                        <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>👥</div>
                        <h3 style={{ fontSize: '2.5rem', margin: 0 }}>{stats.total_users}</h3>
                        <p style={{ color: 'var(--color-text-muted)', margin: 0 }}>Enrolled Users</p>
                    </div>
                    <div className="glass-card text-center">
                        <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>🎯</div>
                        <h3 style={{ fontSize: '2.5rem', margin: 0 }}>{(stats.recognition_threshold * 100).toFixed(0)}%</h3>
                        <p style={{ color: 'var(--color-text-muted)', margin: 0 }}>Recognition Threshold</p>
                    </div>
                </div>
            )}

            {/* Action Cards */}
            <div className="grid grid-2 mb-2">
                <Link to="/enroll" style={{ textDecoration: 'none' }}>
                    <div className="glass-card" style={{ cursor: 'pointer', height: '100%' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>👤</div>
                        <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Enroll User</h3>
                        <p style={{ color: 'var(--color-text-secondary)', margin: 0 }}>
                            Enroll your face with explicit consent
                        </p>
                    </div>
                </Link>

                <Link to="/recognize" style={{ textDecoration: 'none' }}>
                    <div className="glass-card" style={{ cursor: 'pointer', height: '100%' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
                        <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Recognize Face</h3>
                        <p style={{ color: 'var(--color-text-secondary)', margin: 0 }}>
                            Compare a live camera capture with consented enrollments
                        </p>
                    </div>
                </Link>

                <Link to="/users" style={{ textDecoration: 'none' }}>
                    <div className="glass-card" style={{ cursor: 'pointer', height: '100%' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📋</div>
                        <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Manage Users</h3>
                        <p style={{ color: 'var(--color-text-secondary)', margin: 0 }}>
                            View and manage all enrolled users
                        </p>
                    </div>
                </Link>

                <div className="glass-card" style={{ height: '100%' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚙️</div>
                    <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Features</h3>
                    <ul style={{ color: 'var(--color-text-secondary)', paddingLeft: '1.25rem', margin: 0 }}>
                        <li>OpenCV Haar face detection</li>
                        <li>Spatial Local Binary Pattern (LBP) descriptors</li>
                        <li>Encrypted face descriptors in SQLite</li>
                        <li>CPU-only demo matching</li>
                    </ul>
                </div>
            </div>

            {/* Info Section */}
            <div className="glass-card">
                <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>🚀 About HelloFace</h3>
                <p style={{ color: 'var(--color-text-secondary)', lineHeight: '1.8' }}>
                    PrivacyFace is a lightweight, consent-based face matching prototype. It uses OpenCV Haar detection and spatial LBP descriptors to compare enrolled faces. This is an educational demo, not a high-security identity verification system; results can vary with lighting, pose, and camera quality.
                </p>
                <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                    <span className="badge">🆓 100% Free</span>
                    <span className="badge">🔒 Privacy-First</span>
                    <span className="badge">💻 CPU-Optimized</span>
                    <span className="badge">🌐 Open Source</span>
                </div>
            </div>
        </div>
    );
};

export default Home;
