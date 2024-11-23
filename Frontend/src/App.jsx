import React, { useRef, useEffect, useState } from 'react';
import { Layout, Typography, Card, Alert, Row, Col, Statistic, ConfigProvider, theme, Modal, Button, Radio, Space, Progress } from 'antd';
import { UserOutlined, WarningOutlined, CameraOutlined, AudioOutlined, WifiOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { ReactInternetSpeedMeter } from "react-internet-meter";
import "react-internet-meter/dist/index.css";
import * as faceapi from 'face-api.js';

const { Header, Content, Footer } = Layout;
const { Title, Text } = Typography;
const { darkAlgorithm } = theme;

const questions = [
  {
    id: 1,
    question: "What is the capital of France?",
    options: ["London", "Berlin", "Paris", "Madrid"],
    correctAnswer: "Paris"
  },
  {
    id: 2,
    question: "Which planet is known as the Red Planet?",
    options: ["Mars", "Venus", "Jupiter", "Saturn"],
    correctAnswer: "Mars"
  },
  {
    id: 3,
    question: "What is the largest mammal in the world?",
    options: ["African Elephant", "Blue Whale", "Giraffe", "Hippopotamus"],
    correctAnswer: "Blue Whale"
  }
];

function SystemCheck({ onAllChecksPass }) {
  const [webcamCheck, setWebcamCheck] = useState(false);
  const [audioCheck, setAudioCheck] = useState(false);
  const [internetCheck, setInternetCheck] = useState(false);
  const [wifiSpeed, setWifiSpeed] = useState("Checking ... ");
  const videoRef = useRef(null);

  useEffect(() => {
    checkWebcam();
    checkAudio();
  }, []);

  useEffect(() => {
    if (webcamCheck && audioCheck && internetCheck) {
      onAllChecksPass();
    }
  }, [webcamCheck, audioCheck, internetCheck, onAllChecksPass]);

  const checkWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setWebcamCheck(true);
    } catch (err) {
      console.error("Error accessing webcam:", err);
      setWebcamCheck(false);
    }
  };

  const checkAudio = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
      setAudioCheck(true);
    } catch (err) {
      console.error("Error accessing audio:", err);
      setAudioCheck(false);
    }
  };

  return (
    <Card title="System Check" bordered={false}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Text>Webcam Check: {webcamCheck ? <CheckCircleOutlined style={{ color: 'green' }} /> : <CloseCircleOutlined style={{ color: 'red' }} />}</Text>
          {webcamCheck && <video ref={videoRef} autoPlay muted style={{ width: '100%', marginTop: '10px' }} />}
        </div>
        <div>
          <Text>Audio Check: {audioCheck ? <CheckCircleOutlined style={{ color: 'green' }} /> : <CloseCircleOutlined style={{ color: 'red' }} />}</Text>
        </div>
        <div>
          <Text>Internet Speed: {wifiSpeed} Mbps</Text>
          <ReactInternetSpeedMeter
            txtSubHeading={"Internet is too slow " + wifiSpeed + " MB/s"}
            outputType="alert"
            customClassName={null}
            txtMainHeading="Oops..."
            pingInterval={3000}
            thresholdUnit="megabyte"
            threshold={8}
            imageUrl="https://www.sammobile.com/wp-content/uploads/2019/03/keyguard_default_wallpaper_silver.png"
            downloadSize="2550420"
            callbackFunctionOnNetworkDown={(speed) => console.log(`Internet speed is down ${speed}`)}
            callbackFunctionOnNetworkTest={(speed) => {
              setWifiSpeed(speed);
              setInternetCheck(speed >= 8);
            }}
          />
          <Progress percent={Math.min(wifiSpeed * 10, 100)} status={internetCheck ? "success" : "exception"} />
        </div>
      </Space>
    </Card>
  );
}

export default function SecureExamApp() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [snapshots, setSnapshots] = useState([]);
  const [noFaceDuration, setNoFaceDuration] = useState(0);
  const [multipleFacesDuration, setMultipleFacesDuration] = useState(0);
  const [countdown, setCountdown] = useState(5);
  const [faceCount, setFaceCount] = useState(0);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('info');
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [showWarningModal, setShowWarningModal] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [systemCheckPassed, setSystemCheckPassed] = useState(false);
  const [examStarted, setExamStarted] = useState(false);

  let countdownInterval;

  useEffect(() => {
    if (examStarted) {
      document.addEventListener('fullscreenchange', handleFullscreenChange);
      document.addEventListener('keydown', handleKeyDown);
      document.addEventListener('contextmenu', handleContextMenu);
      window.addEventListener('beforeunload', handleBeforeUnload);

      return () => {
        document.removeEventListener('fullscreenchange', handleFullscreenChange);
        document.removeEventListener('keydown', handleKeyDown);
        document.removeEventListener('contextmenu', handleContextMenu);
        window.removeEventListener('beforeunload', handleBeforeUnload);
      };
    }
  }, [examStarted]);

  useEffect(() => {
    if (examStarted) {
      startVideo();
      loadModels();
    }
  }, [examStarted]);

  useEffect(() => {
    if (noFaceDuration >= 15 || multipleFacesDuration >= 15) {
      startCountdown();
    }
  }, [noFaceDuration, multipleFacesDuration]);

  const startVideo = () => {
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((currentStream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = currentStream;
        }
      })
      .catch((err) => {
        console.log(err);
        setMessage('Failed to access camera');
        setMessageType('error');
      });
  };

  const loadModels = () => {
    Promise.all([
      faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
      faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
      faceapi.nets.faceRecognitionNet.loadFromUri('/models'),
      faceapi.nets.faceExpressionNet.loadFromUri('/models'),
    ]).then(() => {
      faceMyDetect();
    });
  };

  const takeSnapshot = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      canvas.getContext('2d').drawImage(videoRef.current, 0, 0);
      const dataUrl = canvas.toDataURL('image/jpeg');
      setSnapshots((prev) => [...prev, dataUrl]);
    }
  };

  const faceMyDetect = () => {
    let noFaceCount = 0;
    const detectionInterval = setInterval(async () => {
      if (videoRef.current && canvasRef.current) {
        const detections = await faceapi
          .detectAllFaces(videoRef.current, new faceapi.TinyFaceDetectorOptions())
          .withFaceLandmarks()
          .withFaceExpressions();

        setFaceCount(detections.length);

        if (detections.length === 0) {
          noFaceCount++;
          setNoFaceDuration((prev) => prev + 1);
          setMultipleFacesDuration(0);
          setMessage('No face detected');
          setMessageType('warning');
          if (noFaceCount === 3) {
            takeSnapshot();
            noFaceCount = 0;
          }
        } else if (detections.length > 1) {
          setMultipleFacesDuration((prev) => prev + 1);
          setNoFaceDuration(0);
          setMessage('Multiple faces detected');
          setMessageType('error');
          takeSnapshot();
        } else {
          setMessage('Face detected');
          setMessageType('info');
          noFaceCount = 0;
          setNoFaceDuration(0);
          setMultipleFacesDuration(0);
          clearInterval(countdownInterval);
          setCountdown(5);
        }

        canvasRef.current.innerHTML = faceapi.createCanvasFromMedia(videoRef.current);
        faceapi.matchDimensions(canvasRef.current, {
          width: canvasRef.current.width,
          height: canvasRef.current.height,
        });

        const resized = faceapi.resizeResults(detections, {
          width: canvasRef.current.width,
          height: canvasRef.current.height,
        });

        faceapi.draw.drawDetections(canvasRef.current, resized);
        faceapi.draw.drawFaceLandmarks(canvasRef.current, resized);
        faceapi.draw.drawFaceExpressions(canvasRef.current, resized);
      }
    }, 1000);
  };

  const startCountdown = () => {
    countdownInterval = setInterval(() => {
      setCountdown((prev) => {
        if (prev === 1) {
          clearInterval(countdownInterval);
          endExam();
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleFullscreenChange = () => {
    setIsFullScreen(!!document.fullscreenElement);
    if (!document.fullscreenElement) {
      setShowWarningModal(true);
    }
  };

  const handleKeyDown = (e) => {
    if (
      e.key === 'F11' ||
      (e.ctrlKey && e.shiftKey && e.key === 'I') ||
      (e.ctrlKey && e.shiftKey && e.key === 'C') ||
      (e.ctrlKey && e.key === 'u')
    ) {
      e.preventDefault();
      setShowWarningModal(true);
    }
  };

  const handleContextMenu = (e) => {
    e.preventDefault();
    setShowWarningModal(true);
  };

  const handleBeforeUnload = (e) => {
    e.preventDefault();
    e.returnValue = '';
  };

  const enterFullScreen = () => {
    const elem = document.documentElement;
    if (elem.requestFullscreen) {
      elem.requestFullscreen();
    }
  };

  const exitFullScreen = () => {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  };

  const endExam = () => {
    exitFullScreen();
    alert('Exam terminated');
    window.location.reload();
  };

  const handleModalOk = () => {
    setShowWarningModal(false);
    enterFullScreen();
  };

  const handleModalCancel = () => {
    setShowWarningModal(false);
    endExam();
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setSelectedAnswer('');
    } else {
      alert('Exam completed!');
      endExam();
    }
  };

  const handleStartExam = () => {
    enterFullScreen();
    setExamStarted(true);
  };

  return (
    <ConfigProvider
      theme={{
        algorithm: darkAlgorithm,
        token: {
          colorBgContainer: '#141414',
          colorBgElevated: '#1f1f1f',
          colorBgLayout: '#000000',
        },
      }}
    >
      <Layout style={{ minHeight: '100vh' }}>
        <Header style={{ background: '#141414', padding: '0 16px' }}>
          <Title level={3} style={{ color: '#fff', margin: '16px 0' }}>
            Secure Exam App
          </Title>
        </Header>
        <Content style={{ padding: '24px' }}>
          {!examStarted ? (
            <Row justify="center" align="middle" style={{ minHeight: 'calc(100vh - 64px - 48px)' }}>
              <Col xs={24} sm={20} md={16} lg={12}>
                <SystemCheck onAllChecksPass={() => setSystemCheckPassed(true)} />
                <Button
                  type="primary"
                  onClick={handleStartExam}
                  disabled={!systemCheckPassed}
                  style={{ marginTop: '20px', width: '100%' }}
                >
                  Start Exam
                </Button>
              </Col>
            </Row>
          ) : (
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={16}>
                <Card title="Exam Question" bordered={false} style={{ height: '100%' }}>
                  <Text strong>{questions[currentQuestionIndex].question}</Text>
                  <Radio.Group
                    onChange={(e) => setSelectedAnswer(e.target.value)}
                    value={selectedAnswer}
                    style={{ display: 'block', marginTop: '16px' }}
                  >
                    <Space direction="vertical">
                      {questions[currentQuestionIndex].options.map((option) => (
                        <Radio key={option} value={option}>
                          {option}
                        </Radio>
                      ))}
                    </Space>
                  </Radio.Group>
                  <Button
                    type="primary"
                    onClick={handleNextQuestion}
                    disabled={!selectedAnswer}
                    style={{ marginTop: '16px' }}
                  >
                    {currentQuestionIndex < questions.length - 1 ? 'Next Question' : 'Finish Exam'}
                  </Button>
                </Card>
              </Col>
              <Col xs={24} lg={8}>
                <Card bordered={false} title="Proctoring">
                  <div style={{ position: 'relative', marginBottom: '16px' }}>
                    <video ref={videoRef} autoPlay muted style={{ width: '100%' }} />
                    <canvas
                      ref={canvasRef}
                      style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
                    />
                  </div>
                  <Alert message={message} type={messageType} showIcon style={{ marginBottom: '16px' }} />
                  <Row gutter={[16, 16]}>
                    <Col span={12}>
                      <Statistic title="Face Count" value={faceCount} prefix={<UserOutlined />} />
                    </Col>
                    <Col span={12}>
                      <Statistic
                        title="No Face Duration"
                        value={noFaceDuration}
                        prefix={<WarningOutlined />}
                        suffix="s"
                      />
                    </Col>
                  </Row>
                  {(noFaceDuration >= 15 || multipleFacesDuration >= 15) && (
                    <Alert
                      message={`Warning: Exam will terminate in ${countdown} seconds`}
                      type="error"
                      showIcon
                      style={{ marginTop: '16px' }}
                    />
                  )}
                </Card>
              </Col>
            </Row>
          )}
          {snapshots.length > 0 && (
            <Card title="Malpractice Snapshots" bordered={false} style={{ marginTop: '24px' }}>
              <Row gutter={[16, 16]}>
                {snapshots.map((snapshot, index) => (
                  <Col key={index} xs={24} sm={12} md={8} lg={6}>
                    <img src={snapshot} alt={`Snapshot ${index + 1}`} />
                  </Col>
                ))}
              </Row>
            </Card>
          )}
        </Content>
        <Footer style={{ textAlign: 'center', background: '#141414', color: '#fff' }}>
          Secure Exam App ©{new Date().getFullYear()} Created by hexaware
        </Footer>
      </Layout>
      <Modal
        title="Warning"
        open={showWarningModal}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        okText="Go back to exam"
        cancelText="End exam"
      >
        <p>You are trying to move out of the exam screen. Please choose an option:</p>
      </Modal>
    </ConfigProvider>
  );
}
