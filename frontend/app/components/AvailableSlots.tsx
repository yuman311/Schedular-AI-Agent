'use client';

interface Slot {
  start: string;
  end: string;
  formatted_start: string;
  formatted_end: string;
  duration_minutes: number;
}

interface AvailableSlotsProps {
  slots: Slot[];
  onSelectSlot: (slot: Slot) => void;
}

export default function AvailableSlots({ slots, onSelectSlot }: AvailableSlotsProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Available Time Slots</h2>
      
      {slots.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          No slots available yet. Ask the AI to search for meeting times.
        </div>
      ) : (
        <div className="space-y-3 max-h-[600px] overflow-y-auto">
          {slots.map((slot, index) => (
            <div
              key={index}
              className="border border-gray-200 rounded-lg p-4 hover:bg-blue-50 transition cursor-pointer"
              onClick={() => onSelectSlot(slot)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-gray-800">
                    {slot.formatted_start}
                  </p>
                  <p className="text-sm text-gray-600">
                    Duration: {slot.duration_minutes} minutes
                  </p>
                  <p className="text-sm text-gray-500">
                    Ends at {slot.formatted_end}
                  </p>
                </div>
                <button
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectSlot(slot);
                  }}
                >
                  Book
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
