import { useState, useEffect, useRef } from 'react';
import { message } from 'antd';
import HUD from './HUD';
import RadarMap from './RadarMap';
import IncidentFeed from './IncidentFeed';
import ResourceBay from './ResourceBay';
import { ALL_SCENARIOS, RESOURCES, ALL_RESOURCES } from '../scenarios/scenarioData';
import '../../styles/game.css'; 

const GLOBAL_EVENTS = [
  { name: 'Heavy Rain', effect: 'Slowing dispatch times.' },
  { name: 'Traffic Jam', effect: 'Resources delayed.' },
  { name: 'GPS Error', effect: 'Routing malfunction.' },
  { name: 'Power Failure', effect: 'Command systems flickering.' },
];

export default function CommandCenter({ sessionId, currentLevel, onLogEvent, onLevelComplete }) {
  const [activeIncidents, setActiveIncidents] = useState([]);
  const [availableResources, setAvailableResources] = useState([...ALL_RESOURCES]);
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);
  const [notifications, setNotifications] = useState(['System initialized. Waiting for emergencies...']);
  
  const [gameStats, setGameStats] = useState({
    incidentsResolved: 0,
    citizensSaved: 0,
    livesLost: 0,
  });

  const scenarios = ALL_SCENARIOS[currentLevel] || [];
  const scenarioIndex = useRef(0);
  const engineTimer = useRef(null);
  const eventTriggered = useRef(false);

  // Initialize Level
  useEffect(() => {
    addNotification(`Module ${currentLevel} started. Stay alert.`);
    scenarioIndex.current = 0;
    setActiveIncidents([]);
    setAvailableResources([...ALL_RESOURCES]);
    eventTriggered.current = false;
    
    // Log module start
    onLogEvent({
      sessionId,
      module: currentLevel,
      eventType: 'MODULE_STARTED',
    });

    const spawner = setTimeout(() => {
      spawnNextIncident();
    }, 2000);

    return () => clearTimeout(spawner);
  }, [currentLevel]);

  const addNotification = (msg) => {
    setNotifications(prev => [msg, ...prev].slice(0, 5));
  };

  const spawnNextIncident = () => {
    if (scenarioIndex.current >= scenarios.length) return;
    
    const scenario = scenarios[scenarioIndex.current];
    const newIncident = {
      ...scenario,
      spawnTime: Date.now(),
      timeLeft: scenario.timeLimit,
      eta: null,
      dispatched: [],
      status: 'active', // active -> dispatching -> resolved/failed
    };
    
    setActiveIncidents(prev => [...prev, newIncident]);
    addNotification(`EMERGENCY: ${scenario.title}!`);
    
    onLogEvent({
      sessionId,
      module: currentLevel,
      scenarioId: scenario.id,
      eventType: 'SCENARIO_CREATED',
      metadata: { severity: scenario.severity, livesAtRisk: scenario.livesAtRisk }
    });

    scenarioIndex.current++;
    
    // If stress level (Level 2), spawn next one quickly
    if (currentLevel === 2 && scenarioIndex.current < scenarios.length) {
      setTimeout(() => spawnNextIncident(), 3000);
    }
  };

  // Game Loop Tick (every 1 second)
  useEffect(() => {
    engineTimer.current = setInterval(() => {
      // Random Global Event check (2% chance per tick if not already triggered)
      if (!eventTriggered.current && Math.random() < 0.02 && activeIncidents.some(i => i.status === 'active' || i.status === 'dispatching')) {
        eventTriggered.current = true;
        const randomEvt = GLOBAL_EVENTS[Math.floor(Math.random() * GLOBAL_EVENTS.length)];
        addNotification(`SYSTEM ALERT: ${randomEvt.name} - ${randomEvt.effect}`);
        
        // Add ETA penalty to any dispatching incidents
        setActiveIncidents(prev => prev.map(inc => {
          if (inc.status === 'dispatching') {
            return { ...inc, eta: inc.eta + 3 };
          }
          return inc;
        }));
      }

      setActiveIncidents(prev => {
        let allDone = true;
        let anyChanges = false;
        
        const nextIncidents = prev.map(inc => {
          if (inc.status === 'resolved' || inc.status === 'failed') return inc;
          allDone = false;
          anyChanges = true;

          // Process Dispatching Countdown
          if (inc.status === 'dispatching') {
            if (inc.eta <= 1) {
              // Resolve it
              addNotification(`MISSION COMPLETED: ${inc.title}`);
              
              setGameStats(s => ({
                ...s,
                incidentsResolved: s.incidentsResolved + 1,
                citizensSaved: s.citizensSaved + (inc.livesAtRisk || 0),
              }));

              onLogEvent({
                sessionId,
                module: currentLevel,
                scenarioId: inc.id,
                eventType: 'SCENARIO_COMPLETED',
                scenarioOutcome: 'success',
                metadata: { severity: inc.severity, livesAtRisk: inc.livesAtRisk }
              });

              // Return resources
              setAvailableResources(curr => [...curr, ...inc.dispatched]);
              
              if (currentLevel !== 2) {
                setTimeout(() => spawnNextIncident(), 1500);
              }

              return { ...inc, status: 'resolved', eta: 0 };
            }
            return { ...inc, eta: inc.eta - 1 };
          }

          // Process Active Countdown
          let newTimeLeft = inc.timeLeft - 1;
          
          // Level 4 Adaptive Trigger
          if (currentLevel === 4 && inc.dynamicEvent && newTimeLeft === inc.dynamicEvent.triggerTime && !inc.dynamicEventTriggered) {
            addNotification(inc.dynamicEvent.message);
            onLogEvent({
               sessionId,
               module: currentLevel,
               scenarioId: inc.id,
               eventType: 'ADAPTATION_EVENT',
            });
            return {
              ...inc,
              timeLeft: newTimeLeft,
              requiredResources: inc.dynamicEvent.newRequired,
              dynamicEventTriggered: true,
              priority: inc.dynamicEvent.severityEscalation === 'Critical' ? 'critical' : inc.priority,
              severity: inc.dynamicEvent.severityEscalation || inc.severity,
            };
          }

          if (newTimeLeft <= 0) {
            addNotification(`FAILED: ${inc.title} timer expired!`);
            handleIncidentFailure(inc, 'TIMEOUT');
            return { ...inc, status: 'failed', timeLeft: 0 };
          }
          
          return { ...inc, timeLeft: newTimeLeft };
        });

        // Check if level is fully completed
        if (allDone && prev.length > 0 && scenarioIndex.current >= scenarios.length) {
          clearInterval(engineTimer.current);
          onLogEvent({
            sessionId,
            module: currentLevel,
            eventType: 'MODULE_COMPLETED',
          });
          setTimeout(() => onLevelComplete(currentLevel), 1500);
        }

        return anyChanges ? nextIncidents : prev;
      });
    }, 1000);

    return () => clearInterval(engineTimer.current);
  }, [currentLevel, scenarios.length, activeIncidents]);

  const handleIncidentFailure = (incident, reason) => {
    setGameStats(s => ({
      ...s,
      livesLost: s.livesLost + (incident.livesAtRisk || 0),
    }));

    onLogEvent({
      sessionId,
      module: currentLevel,
      scenarioId: incident.id,
      eventType: reason,
      timeout: reason === 'TIMEOUT',
      scenarioOutcome: 'failed',
      metadata: { severity: incident.severity, livesAtRisk: incident.livesAtRisk }
    });
    // Return dispatched resources back to bay
    setAvailableResources(prev => [...prev, ...incident.dispatched]);
    
    if (currentLevel !== 2) {
      setTimeout(() => spawnNextIncident(), 2000);
    }
  };

  const handleIncidentSelect = (id) => {
    setSelectedIncidentId(id);
    onLogEvent({
      sessionId,
      module: currentLevel,
      scenarioId: id,
      eventType: 'INCIDENT_SELECTED',
    });
  };

  const handleResourceDispatch = (resource) => {
    if (!selectedIncidentId) {
      message.warning('Select an incident card first!');
      // Assuming a panic click if they keep clicking resources without selecting
      onLogEvent({ sessionId, module: currentLevel, eventType: 'PANIC_CLICK', panicClicks: 1 });
      return;
    }

    const incident = activeIncidents.find(i => i.id === selectedIncidentId);
    if (!incident || incident.status !== 'active') return;

    onLogEvent({
      sessionId,
      module: currentLevel,
      scenarioId: incident.id,
      eventType: 'RESOURCE_SELECTED',
      selectedResource: resource,
    });

    // Check Level 3 equipment failure randomly (30% chance on first dispatch)
    if (currentLevel === 3 && incident.dispatched.length === 0 && Math.random() < 0.3) {
       addNotification(`FAILURE OCCURRED: ${resource} broke down! Select alternative.`);
       onLogEvent({
         sessionId,
         module: currentLevel,
         scenarioId: incident.id,
         eventType: 'FAILURE_OCCURRED',
         metadata: { failedResource: resource }
       });
       onLogEvent({
         sessionId,
         module: currentLevel,
         scenarioId: incident.id,
         eventType: 'RECOVERY_STARTED',
       });
       return;
    }

    // Assign resource
    setAvailableResources(prev => prev.filter(r => r !== resource));
    
    setActiveIncidents(prev => prev.map(inc => {
      if (inc.id !== selectedIncidentId) return inc;
      
      const newDispatched = [...inc.dispatched, resource];
      
      // Check if requirements met
      const isCorrect = inc.requiredResources.every(r => newDispatched.includes(r)) && 
                        newDispatched.every(r => inc.requiredResources.includes(r));
                        
      const decisionTime = Date.now() - inc.spawnTime;
      
      onLogEvent({
        sessionId,
        module: currentLevel,
        scenarioId: inc.id,
        eventType: 'RESOURCE_DISPATCHED',
        dispatchedUnits: newDispatched,
      });

      if (isCorrect) {
        addNotification(`DISPATCHING: ETA 4 seconds to ${inc.title}`);
        
        onLogEvent({
          sessionId,
          module: currentLevel,
          scenarioId: inc.id,
          eventType: 'CORRECT_DECISION',
          reactionTime: decisionTime,
          decisionTime,
          dispatchedUnits: newDispatched,
          correct: true,
        });

        // If it's module 3, they might have recovered
        if (currentLevel === 3) {
           onLogEvent({
             sessionId,
             module: currentLevel,
             scenarioId: inc.id,
             eventType: 'RECOVERY_COMPLETED',
             recoveryLatency: decisionTime
           });
        }

        // Change status to dispatching
        return { ...inc, dispatched: newDispatched, status: 'dispatching', eta: 4 };
      } else {
        // If they dispatched the WRONG amount (but haven't finished), wait. 
        // We only trigger WRONG_DECISION if they dispatch something completely unrelated.
        if (!inc.requiredResources.includes(resource)) {
          onLogEvent({
            sessionId,
            module: currentLevel,
            scenarioId: inc.id,
            eventType: 'WRONG_DECISION',
            reactionTime: decisionTime,
            decisionTime,
            selectedResource: resource,
            correct: false,
          });
        }
      }
      
      return { ...inc, dispatched: newDispatched };
    }));
  };

  const hudGameStats = {
    ...gameStats,
    activeIncidents: activeIncidents.filter(i => i.status === 'active' || i.status === 'dispatching').length,
    resourcesRemaining: availableResources.length,
  };

  const activeTimeLeft = Math.max(0, ...activeIncidents.filter(i => i.status === 'active').map(i => i.timeLeft));

  return (
    <div className="command-center">
      <HUD 
        level={currentLevel} 
        notifications={notifications} 
        gameStats={hudGameStats}
        timeRemaining={activeTimeLeft || undefined}
      />
      <div className="game-grid">
        <RadarMap incidents={activeIncidents} />
        <IncidentFeed 
          incidents={activeIncidents} 
          selectedId={selectedIncidentId}
          onSelect={handleIncidentSelect} 
        />
      </div>
      <ResourceBay 
        available={availableResources} 
        onDispatch={handleResourceDispatch} 
        hasSelection={!!selectedIncidentId}
      />
    </div>
  );
}
