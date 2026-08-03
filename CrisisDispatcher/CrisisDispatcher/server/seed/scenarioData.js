/**
 * Emergency scenario data for the Crisis Dispatcher Command Center.
 * 12 distinct emergency types distributed across 4 difficulty levels (Modules).
 */

const RESOURCES = {
  AMBULANCE: 'Ambulance',
  FIRE_TRUCK: 'Fire Truck',
  POLICE: 'Police Unit',
  RESCUE: 'Rescue Team',
};

const PRIORITIES = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
};

const SEVERITIES = {
  LOW: 'Low',
  MEDIUM: 'Medium',
  HIGH: 'High',
  CRITICAL: 'Critical',
};

// All available resources for the game engine to render in the bay
const ALL_RESOURCES = [RESOURCES.AMBULANCE, RESOURCES.FIRE_TRUCK, RESOURCES.POLICE, RESOURCES.RESCUE];

/**
 * Module 1 — Baseline Assessment
 * Single incidents, generous timers.
 */
const MODULE_1_SCENARIOS = [
  {
    id: 'm1_s1',
    type: 'Road Accident',
    title: 'Minor Intersection Collision',
    description: 'A two-vehicle collision at a major intersection. One driver is complaining of neck pain. Traffic is building up.',
    location: '5th Ave & Main St',
    severity: SEVERITIES.LOW,
    livesAtRisk: 2,
    priority: PRIORITIES.LOW,
    timeLimit: 30, // seconds
    requiredResources: [RESOURCES.AMBULANCE, RESOURCES.POLICE],
    module: 1,
  },
  {
    id: 'm1_s2',
    type: 'Medical Emergency',
    title: 'Elderly Collapse',
    description: 'An elderly citizen has collapsed in a public park. Bystanders report they are conscious but confused. No visible trauma.',
    location: 'Centennial Park',
    severity: SEVERITIES.MEDIUM,
    livesAtRisk: 1,
    priority: PRIORITIES.MEDIUM,
    timeLimit: 25,
    requiredResources: [RESOURCES.AMBULANCE],
    module: 1,
  },
  {
    id: 'm1_s3',
    type: 'Electrical Failure',
    title: 'Sparking Transformer',
    description: 'A street transformer is sparking violently. A small crowd has gathered. High risk of fire and electrocution.',
    location: 'Elm Street Residential',
    severity: SEVERITIES.HIGH,
    livesAtRisk: 5,
    priority: PRIORITIES.HIGH,
    timeLimit: 25,
    requiredResources: [RESOURCES.FIRE_TRUCK, RESOURCES.POLICE],
    module: 1,
  }
];

/**
 * Module 2 — Stress Induction
 * Simultaneous incidents, short timers.
 */
const MODULE_2_SCENARIOS = [
  {
    id: 'm2_s1',
    type: 'Building Fire',
    title: 'Apartment Complex Fire',
    description: 'Flames visible on the 3rd floor. Residents are evacuating but some may be trapped. Smoke is filling the hallways.',
    location: 'Sunset Apartments',
    severity: SEVERITIES.CRITICAL,
    livesAtRisk: 15,
    priority: PRIORITIES.CRITICAL,
    timeLimit: 15,
    requiredResources: [RESOURCES.FIRE_TRUCK, RESOURCES.AMBULANCE, RESOURCES.RESCUE],
    module: 2,
  },
  {
    id: 'm2_s2',
    type: 'Gas Leak',
    title: 'Underground Pipe Rupture',
    description: 'Strong smell of gas in a commercial district. Immediate evacuation required before a potential explosion.',
    location: 'Downtown Market',
    severity: SEVERITIES.CRITICAL,
    livesAtRisk: 40,
    priority: PRIORITIES.CRITICAL,
    timeLimit: 12,
    requiredResources: [RESOURCES.FIRE_TRUCK, RESOURCES.POLICE],
    module: 2,
  },
  {
    id: 'm2_s3',
    type: 'Train Derailment',
    title: 'Passenger Train Off Tracks',
    description: 'A commuter train has derailed near the station. Multiple cars overturned. Mass casualties expected.',
    location: 'Central Station',
    severity: SEVERITIES.CRITICAL,
    livesAtRisk: 120,
    priority: PRIORITIES.HIGH,
    timeLimit: 18,
    requiredResources: [RESOURCES.AMBULANCE, RESOURCES.FIRE_TRUCK, RESOURCES.RESCUE, RESOURCES.POLICE],
    module: 2,
  },
];

/**
 * Module 3 — Failure & Recovery
 * Equipment failures occur upon dispatch.
 */
const MODULE_3_SCENARIOS = [
  {
    id: 'm3_s1',
    type: 'Flood',
    title: 'Flash Flood Rescue',
    description: 'River banks have overflowed. Families are trapped on the roof of their homes. Water levels rising rapidly.',
    location: 'Riverbank Suburbs',
    severity: SEVERITIES.CRITICAL,
    livesAtRisk: 8,
    priority: PRIORITIES.CRITICAL,
    timeLimit: 22,
    requiredResources: [RESOURCES.RESCUE, RESOURCES.AMBULANCE],
    module: 3,
    setback: {
      message: 'Rescue boats unavailable due to prior deployment! Use Police for perimeter control while waiting for airlift.',
      newRequired: [RESOURCES.POLICE, RESOURCES.AMBULANCE],
    }
  },
  {
    id: 'm3_s2',
    type: 'Building Collapse',
    title: 'Warehouse Roof Cave-in',
    description: 'An old warehouse roof collapsed during a storm. Night shift workers are unaccounted for under the rubble.',
    location: 'Industrial District',
    severity: SEVERITIES.CRITICAL,
    livesAtRisk: 12,
    priority: PRIORITIES.CRITICAL,
    timeLimit: 20,
    requiredResources: [RESOURCES.RESCUE, RESOURCES.AMBULANCE, RESOURCES.FIRE_TRUCK],
    module: 3,
    setback: {
      message: 'Ambulance broke down en route! Rely on Rescue Team paramedics on site.',
      newRequired: [RESOURCES.RESCUE, RESOURCES.FIRE_TRUCK],
    }
  },
  {
    id: 'm3_s3',
    type: 'Bridge Collapse',
    title: 'Suspension Cable Snapped',
    description: 'A major bridge cable has snapped, trapping cars on the suspended section. High wind conditions.',
    location: 'Bay Bridge',
    severity: SEVERITIES.CRITICAL,
    livesAtRisk: 25,
    priority: PRIORITIES.CRITICAL,
    timeLimit: 25,
    requiredResources: [RESOURCES.POLICE, RESOURCES.RESCUE, RESOURCES.FIRE_TRUCK],
    module: 3,
    setback: {
      message: 'Fire Truck delayed by traffic jam! Use Police and Rescue to stabilize the scene.',
      newRequired: [RESOURCES.POLICE, RESOURCES.RESCUE],
    }
  },
];

/**
 * Module 4 — Adaptive Challenge
 * Mid-countdown dynamic events that escalate the situation.
 */
const MODULE_4_SCENARIOS = [
  {
    id: 'm4_s1',
    type: 'Industrial Accident',
    title: 'Factory Explosion',
    description: 'Explosion at a manufacturing plant. Structural damage and potential fires. Initial assessment ongoing.',
    location: 'Sector 7 Plant',
    severity: SEVERITIES.HIGH,
    livesAtRisk: 10,
    priority: PRIORITIES.HIGH,
    timeLimit: 28,
    requiredResources: [RESOURCES.FIRE_TRUCK, RESOURCES.RESCUE],
    module: 4,
    dynamicEvent: {
      triggerTime: 14, // seconds remaining when this triggers
      message: 'ENVIRONMENTAL HAZARD: Chemical tanks ruptured! Toxic fumes spreading. Evacuate immediately.',
      newRequired: [RESOURCES.FIRE_TRUCK, RESOURCES.RESCUE, RESOURCES.POLICE, RESOURCES.AMBULANCE],
      severityEscalation: SEVERITIES.CRITICAL,
    }
  },
  {
    id: 'm4_s2',
    type: 'Earthquake',
    title: 'Magnitude 6.2 Tremor',
    description: 'Major tremor felt across the city. Power grids failing. Multiple distress calls from the downtown sector.',
    location: 'City Wide',
    severity: SEVERITIES.CRITICAL,
    livesAtRisk: 200,
    priority: PRIORITIES.CRITICAL,
    timeLimit: 25,
    requiredResources: [RESOURCES.RESCUE, RESOURCES.POLICE],
    module: 4,
    dynamicEvent: {
      triggerTime: 12,
      message: 'COMMUNICATION FAILURE: Radio towers down. Fires breaking out in sector 4. Send all available Fire units!',
      newRequired: [RESOURCES.RESCUE, RESOURCES.POLICE, RESOURCES.FIRE_TRUCK],
    }
  },
  {
    id: 'm4_s3',
    type: 'Chemical Leak',
    title: 'Train Derailment Spillage',
    description: 'A cargo train derailed. Unknown chemicals spilling near a residential water supply. Area needs containment.',
    location: 'Outskirts Crossing',
    severity: SEVERITIES.HIGH,
    livesAtRisk: 50,
    priority: PRIORITIES.HIGH,
    timeLimit: 22,
    requiredResources: [RESOURCES.FIRE_TRUCK, RESOURCES.POLICE],
    module: 4,
    dynamicEvent: {
      triggerTime: 11,
      message: 'SITUATION ESCALATION: Chemical identified as highly toxic and volatile. Medical teams required for exposed citizens.',
      newRequired: [RESOURCES.FIRE_TRUCK, RESOURCES.POLICE, RESOURCES.AMBULANCE],
      severityEscalation: SEVERITIES.CRITICAL,
    }
  }
];

const ALL_SCENARIOS = {
  1: MODULE_1_SCENARIOS,
  2: MODULE_2_SCENARIOS,
  3: MODULE_3_SCENARIOS,
  4: MODULE_4_SCENARIOS,
};

module.exports = {
  RESOURCES,
  ALL_RESOURCES,
  PRIORITIES,
  SEVERITIES,
  MODULE_1_SCENARIOS,
  MODULE_2_SCENARIOS,
  MODULE_3_SCENARIOS,
  MODULE_4_SCENARIOS,
  ALL_SCENARIOS,
};
