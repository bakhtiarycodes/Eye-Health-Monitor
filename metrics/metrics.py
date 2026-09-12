import time
from collections import deque
import math

class EyeMetrics:

    def __init__(self):
        # Times for each blink: store (start_time, end_time)
        self.blink_events = deque(maxlen=100)

        # Count of incomplete blinks
        self.incomplete_blink_count = 0
        self.total_blinks = 0
        self.frame_count = 0

        # EAR threshold for blink detection
        self.ear_threshold = 0.20
        # Full closure required below this EAR; higher minimum = incomplete blink
        self.incomplete_ear_threshold = 0.14
        self.closed_frames = 0

        # FPS of the video
        self.fps = 30

        # Track first blink for rate calculation
        self.first_blink_time = None
        self.last_update_time = None

        # For smoothing EAR
        self.ear_buffer = deque(maxlen=3)

        # Track current blink start and deepest closure during the blink
        self.blink_start = None
        self.min_ear_in_blink = None

    # Euclidean distance between two points
    @staticmethod
    def euclidean_distance(p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    # Compute Eye Aspect Ratio
    def compute_ear(self, eye_points):
        p1, p2, p3, p4, p5, p6 = eye_points
        horizontal = self.euclidean_distance(p1, p4)
        if horizontal == 0:
            return 0.0
        ear = (self.euclidean_distance(p2, p6) +
               self.euclidean_distance(p3, p5)) / (2.0 * horizontal)
        return ear

    # Main update function (API preserved)
    def update(self, left_eye, right_eye):
        self.frame_count += 1
        current_time = time.time()
        self.last_update_time = current_time

        left_ear = self.compute_ear(left_eye)
        right_ear = self.compute_ear(right_eye)
        raw_ear = (left_ear + right_ear) / 2.0

        # Smooth EAR for display only; blink detection uses raw values
        self.ear_buffer.append(raw_ear)
        display_ear = sum(self.ear_buffer) / len(self.ear_buffer)

        blinked = False

        # Event-based blink detection
        if raw_ear < self.ear_threshold:
            self.closed_frames += 1
            if self.blink_start is None:
                self.blink_start = current_time
                self.min_ear_in_blink = raw_ear
            else:
                self.min_ear_in_blink = min(self.min_ear_in_blink, raw_ear)
        else:
            if self.blink_start is not None:
                duration = current_time - self.blink_start
                if duration < 0.05:
                    self.incomplete_blink_count += 1
                elif self.min_ear_in_blink > self.incomplete_ear_threshold:
                    # Eyelids closed partially but not fully
                    self.incomplete_blink_count += 1
                else:
                    self.blink_events.append((self.blink_start, current_time))
                    if self.first_blink_time is None:
                        self.first_blink_time = self.blink_start
                    self.total_blinks += 1
                    blinked = True
                self.blink_start = None
                self.min_ear_in_blink = None
            self.closed_frames = 0

        metrics = {}
        metrics['EAR'] = display_ear

        # Blink Duration (average)
        if self.blink_events:
            durations = [end - start for start, end in self.blink_events]
            metrics['Blink Duration'] = sum(durations) / len(durations)
        else:
            metrics['Blink Duration'] = 0

        # Incomplete Blink Ratio
        total_blinks = len(self.blink_events) + self.incomplete_blink_count
        metrics['Incomplete Blink Ratio'] = (
            self.incomplete_blink_count / total_blinks if total_blinks > 0 else 0
        )

        # PERCLOS - sliding window 60s
        window_duration = 60.0
        window_start = current_time - window_duration
        closed_time = 0
        for start, end in self.blink_events:
            overlap_start = max(start, window_start)
            overlap_end = min(end, current_time)
            if overlap_start < overlap_end:
                closed_time += overlap_end - overlap_start
        total_time = min(window_duration, self.frame_count / self.fps)
        metrics['PERCLOS'] = (closed_time / total_time) * 100 if total_time > 0 else 0

        # Blink Rate - number of blinks in last 60s
        blinks_in_window = sum(1 for start, end in self.blink_events if end >= window_start)
        if self.blink_events:
            time_span = min(window_duration, current_time - self.blink_events[0][0])
        else:
            time_span = 0
        metrics['Blink Rate'] = (blinks_in_window / time_span) * 60 if time_span > 0 else 0

        # Inter Blink Interval (IBI) - seconds since previous blink ended
        if len(self.blink_events) >= 2:
            metrics['IBI'] = self.blink_events[-1][1] - self.blink_events[-2][1]
        elif len(self.blink_events) == 1:
            metrics['IBI'] = current_time - self.blink_events[-1][1]
        else:
            metrics['IBI'] = 0

        return metrics, blinked
    