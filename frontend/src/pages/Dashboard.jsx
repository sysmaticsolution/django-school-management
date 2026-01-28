import React from 'react';
import { Row, Col, Card, Statistic, Table, Typography } from 'antd';
import { UserOutlined, TeamOutlined, DollarOutlined, CalendarOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

const { Title } = Typography;

const Dashboard = () => {
    // Using dummy data for now, replace with API calls later
    const stats = [
        { title: 'Total Students', value: 1250, icon: <UserOutlined />, color: '#3f8600' },
        { title: 'Total Staff', value: 85, icon: <TeamOutlined />, color: '#1890ff' },
        { title: 'Fee Collection', value: '₹ 12.5L', icon: <DollarOutlined />, color: '#cf1322' },
        { title: 'Attendance Today', value: '94%', icon: <CalendarOutlined />, color: '#faad14' },
    ];

    return (
        <div>
            <Title level={2}>Admin Dashboard</Title>

            <Row gutter={[16, 16]}>
                {stats.map((stat, index) => (
                    <Col xs={24} sm={12} md={6} key={index}>
                        <Card>
                            <Statistic
                                title={stat.title}
                                value={stat.value}
                                prefix={<span style={{ color: stat.color, marginRight: 10 }}>{stat.icon}</span>}
                            />
                        </Card>
                    </Col>
                ))}
            </Row>

            <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
                <Col xs={24} md={12}>
                    <Card title="Recent Announcements">
                        <p>Parent Teacher Meeting on 10th Feb</p>
                        <p>Sports Day scheduled for next month</p>
                        <p>Exam results declared for Class 10</p>
                    </Card>
                </Col>
                <Col xs={24} md={12}>
                    <Card title="Fee Defaulters">
                        <p>Class 10-A: 5 students</p>
                        <p>Class 9-B: 3 students</p>
                        <p>Class 12-C: 8 students</p>
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

export default Dashboard;
