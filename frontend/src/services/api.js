/**
 * API Service Client — RailFlow AI
 * Connects to FastAPI backend (http://localhost:8000) with robust mock fallback.
 */

const API_BASE = 'http://localhost:8000';

const MOCK_TRAINS = {
  '12951': {
    train_name: "Mumbai Rajdhani Express",
    train_number: "12951",
    predicted_eta_range: {
      min_eta: "17:15",
      max_eta: "17:45",
      min_delay_min: 10,
      max_delay_min: 40,
      expected_delay_min: 18
    },
    current_status: "18 min late",
    delay_reason: "Running 18 min late due to heavy rain and track section congestion near Kota.",
    current_position: {
      station_code: "KOTA",
      station_name: "Kota Junction",
      latitude: 25.2138,
      longitude: 75.8648
    },
    next_station: "Ratlam Junction (RTM)",
    previous_station: "Sawai Madhopur (SWM)",
    historical_reliability_score: 92.4,
    confidence_trend: "Narrowing (High Confidence — Approaching Destination)",
    alternative_trains: []
  },
  '12002': {
    train_name: "Bhopal Shatabdi Express",
    train_number: "12002",
    predicted_eta_range: {
      min_eta: "14:10",
      max_eta: "14:20",
      min_delay_min: 0,
      max_delay_min: 10,
      expected_delay_min: 4
    },
    current_status: "On Time",
    delay_reason: "Minimal delay expected; normal operating speed.",
    current_position: {
      station_code: "AGC",
      station_name: "Agra Cantt",
      latitude: 27.1594,
      longitude: 77.9944
    },
    next_station: "Gwalior Junction (GWL)",
    previous_station: "Mathura Junction (MTJ)",
    historical_reliability_score: 96.8,
    confidence_trend: "Narrowing (High Confidence — Approaching Destination)",
    alternative_trains: []
  },
  '12424': {
    train_name: "Dibrugarh Rajdhani Express",
    train_number: "12424",
    predicted_eta_range: {
      min_eta: "18:40",
      max_eta: "19:20",
      min_delay_min: 25,
      max_delay_min: 65,
      expected_delay_min: 35
    },
    current_status: "35 min late",
    delay_reason: "Running 35 min late due to dense fog and speed restriction near Kanpur.",
    current_position: {
      station_code: "CNB",
      station_name: "Kanpur Central",
      latitude: 26.4537,
      longitude: 80.3512
    },
    next_station: "Prayagraj Junction (PRYJ)",
    previous_station: "Aligarh Junction (ALJN)",
    historical_reliability_score: 84.0,
    confidence_trend: "Moderate Spread (Mid-Journey)",
    alternative_trains: []
  }
};

export async function predictTrainETA(trainId) {
  const cleanId = String(trainId).trim();
  try {
    const res = await fetch(`${API_BASE}/train/${cleanId}/live`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn(`Backend API unreachable (${err.message}). Using mock fallback.`);
  }

  if (MOCK_TRAINS[cleanId]) {
    return MOCK_TRAINS[cleanId];
  }

  return {
    train_name: `Express ${cleanId}`,
    train_number: cleanId,
    predicted_eta_range: {
      min_eta: "16:20",
      max_eta: "16:50",
      min_delay_min: 5,
      max_delay_min: 35,
      expected_delay_min: 15
    },
    current_status: "15 min late",
    delay_reason: "Running 15 min late due to routine signal hold and headway clearance.",
    current_position: {
      station_code: "NDLS",
      station_name: "New Delhi Railway Station",
      latitude: 28.6139,
      longitude: 77.2090
    },
    next_station: "Kanpur Central (CNB)",
    previous_station: "ORIGIN",
    historical_reliability_score: 88.0,
    confidence_trend: "Moderate Spread (Mid-Journey)",
    alternative_trains: []
  };
}

export async function getAlternativeTrainsRoute(trainId) {
  try {
    const res = await fetch(`${API_BASE}/alternatives/${trainId}`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend API unreachable for alternatives. Returning mock.');
  }

  if (trainId === '12424' || trainId === '12951') {
    return {
      delay_minutes: 35,
      reason_type: "conflict",
      blocking_train_id: "12002",
      has_alternative: true,
      alternative_type: "chained",
      direct: null,
      chained: {
        leg_1: {
          train_id: "12004",
          from: "NDLS",
          to: "CNB",
          departure: "18:10",
          predicted_arrival: "22:25"
        },
        leg_2: {
          train_id: "22436",
          from: "CNB",
          to: "MMCT",
          departure: "23:15",
          predicted_arrival: "07:30"
        },
        total_journey_time_minutes: 500
      }
    };
  }

  return {
    delay_minutes: 5,
    reason_type: "operational",
    blocking_train_id: null,
    has_alternative: false,
    alternative_type: null,
    direct: null,
    chained: null
  };
}

export async function getPropagation(sectionId = 'SEC_NDLS_CNB') {
  try {
    const res = await fetch(`${API_BASE}/propagation/${sectionId}`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend API unreachable. Returning mock propagation.');
  }

  return {
    section_id: sectionId,
    total_affected_trains: 2,
    primary_delayed_train: "12951",
    cascaded_delays: [
      {
        train_id: "12002",
        train_name: "Bhopal Shatabdi",
        original_delay_min: 4,
        additional_cascade_delay_min: 10,
        new_projected_delay_min: 14,
        dependency_reason: "Headway block dependency behind Train 12951"
      },
      {
        train_id: "12424",
        train_name: "Dibrugarh Rajdhani",
        original_delay_min: 35,
        additional_cascade_delay_min: 6,
        new_projected_delay_min: 41,
        dependency_reason: "Platform clearance hold at Kanpur"
      }
    ],
    graph_summary: {
      total_nodes: 4,
      total_edges: 3,
      section_id: sectionId,
      corridor_type: "Trunk Main Line",
      bottleneck_severity: "Moderate-High"
    }
  };
}

export async function simulateWhatIf(trainId, addedDelay) {
  try {
    const res = await fetch(`${API_BASE}/whatif`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        train_id: trainId,
        additional_delay_minutes: parseFloat(addedDelay),
        section_id: "SEC_NDLS_CNB"
      }),
      signal: AbortSignal.timeout(3000)
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend API unreachable. Simulating What-If mock.');
  }

  const delayNum = parseFloat(addedDelay) || 10;
  const cascadedDelay1 = Math.round(delayNum * 0.65);
  const cascadedDelay2 = Math.round(delayNum * 0.35);

  return {
    target_train_id: trainId,
    applied_additional_delay_min: delayNum,
    section_id: "SEC_NDLS_CNB",
    total_downstream_trains_affected: 2,
    network_delay_increase_min: delayNum + cascadedDelay1 + cascadedDelay2,
    affected_trains: [
      {
        train_id: "12002",
        train_name: "Bhopal Shatabdi Express",
        original_delay_min: 4,
        additional_cascade_delay_min: cascadedDelay1,
        new_projected_delay_min: 4 + cascadedDelay1,
        dependency_reason: `Headway block clearance behind Train ${trainId}`
      },
      {
        train_id: "12424",
        train_name: "Dibrugarh Rajdhani Express",
        original_delay_min: 35,
        additional_cascade_delay_min: cascadedDelay2,
        new_projected_delay_min: 35 + cascadedDelay2,
        dependency_reason: `Corridor sequence hold behind Train 12002`
      }
    ]
  };
}

export async function getNetworkHealth() {
  try {
    const res = await fetch(`${API_BASE}/network/health`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend API unreachable. Returning mock network health.');
  }

  return {
    timestamp: new Date().toISOString(),
    total_active_trains: 142,
    network_punctuality_rate_pct: 84.5,
    average_delay_minutes: 14.2,
    overall_congestion_index: 0.48,
    top_congested_sections: [
      {
        section_id: "SEC_NDLS_CNB",
        congestion_score: 0.82,
        active_trains_count: 8,
        average_speed_kmh: 42.0,
        status: "Congested / Bottleneck"
      },
      {
        section_id: "SEC_CNB_PRYJ",
        congestion_score: 0.74,
        active_trains_count: 6,
        average_speed_kmh: 51.0,
        status: "Moderate Traffic"
      }
    ],
    high_risk_corridors: [
      "Delhi - Kanpur Trunk Corridor",
      "Howrah - Asansol Industrial Belt",
      "Mumbai - Kalyan Junction Throat"
    ]
  };
}
