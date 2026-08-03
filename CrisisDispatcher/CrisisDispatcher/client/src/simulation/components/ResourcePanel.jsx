import { ALL_RESOURCES, RESOURCE_ICONS } from '../scenarios/scenarioData';

/**
 * ResourcePanel — Selectable resource cards
 */
export default function ResourcePanel({
  selectedResources = [],
  onToggle,
  unavailableResources = [],
  disabled = false,
}) {
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ fontWeight: 600, marginBottom: 8, fontSize: 14 }}>
        🚨 Select Emergency Resources:
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
        {ALL_RESOURCES.map((resource) => {
          const isSelected = selectedResources.includes(resource);
          const isUnavailable = unavailableResources.includes(resource);

          return (
            <div
              key={resource}
              className={`resource-card ${isSelected ? 'selected' : ''} ${isUnavailable ? 'unavailable' : ''}`}
              onClick={() => {
                if (!disabled && !isUnavailable) {
                  onToggle(resource);
                }
              }}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !disabled && !isUnavailable) {
                  onToggle(resource);
                }
              }}
            >
              <div style={{ fontSize: 28, marginBottom: 4 }}>
                {RESOURCE_ICONS[resource]}
              </div>
              <div style={{ fontSize: 12, fontWeight: 600, color: isSelected ? '#1B3A5C' : '#666' }}>
                {resource}
              </div>
              {isUnavailable && (
                <div style={{ fontSize: 10, color: '#DC3545', marginTop: 2 }}>
                  Unavailable
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
