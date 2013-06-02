from collections import deque
from os import path
import multiprocessing as mp
from Queue import Empty as QEmpty  # unfortunately, not in multiprocessing
import time
import Tkinter as tk
import ImageTk
import ttk

import Image as PIL_Image
import numpy

from pqhelper import easy, data, base
_this_path = path.abspath(path.split(__file__)[0])


def _capture_async(async_results_q=None):
    result = easy.capture_solution()
    async_results_q.put(result)


class GUI(object):
    """Provide a common GUI for all PQ game types."""
    def __init__(self):
        # setup the root and tab shell
        self._root = tk.Tk()
        self._root.title('PQ Helper')
        notebook = ttk.Notebook(self._root)
        # setup versus
        versus_tab = ttk.Frame(notebook)
        notebook.add(versus_tab, text='Versus')
        _GenericGameGUI(versus_tab, easy.versus_summaries, time_limit=10.0)
        # setup capture
        capture_tab = ttk.Frame(notebook)
        notebook.add(capture_tab, text='Capture')
        _GenericGameGUI(capture_tab, _capture_async, time_limit=120.0)
        # done
        notebook.pack()
        self._root.mainloop()


class _GenericGameGUI(object):
    """Common GUI elements for every game type."""
    _TILE_SHAPE = (30, 30, 3)
    _POLL_PERIOD_MILLISECONDS = 100

    # Internal Setup, Configuration, Modification, etc.
    def __init__(self, base, analysis_function, time_limit=5.0):
        """Setup the common UI elements and behavior for a PQ Game UI.

        Arguments:
        - base: a tkinter base element in which to create parts
        """
        self._base = base
        self._analysis_function = analysis_function
        self._tile_images = self._create_tile_images()
        self._analyze_start_time = None
        self.time_limit = time_limit
        self.summaries = None
        self._parts = self._setup_parts(self._base)

    @property
    def summaries(self):
        return self._summaries

    @summaries.setter
    def summaries(self, sequence):
        sequence = sequence or [None]
        self._summaries = deque(sequence)

    def _create_tile_images(self):
        images = dict()
        for character, image in data.tile_templates.items():
            tile_size = self._TILE_SHAPE[0:2]
            resized = data.cv2.resize(image, tile_size,
                                      interpolation=data.cv2.INTER_AREA)
            images[character] = resized
        return images

    def _setup_parts(self, base):
        parts = dict()
        # top row: image area
        first_row = tk.Frame(base)
        first_row.pack(anchor=tk.W)
        blank_image_cv = self._create_board_image_cv()
        blank_image_tk = self._convert_cv_to_tk(blank_image_cv)
        imagelabel = tk.Label(first_row)
        #keep a reference or it will be garbage collected
        imagelabel._blank_image = blank_image_tk
        imagelabel._board_image = None
        imagelabel.config(image=imagelabel._blank_image)
        imagelabel.pack()
        parts['board image label'] = imagelabel
        # second row: analyze button and navigation
        second_row = tk.Frame(base)
        second_row.pack(anchor=tk.N, expand=1, fill=tk.X)
        analyze_button = tk.Button(second_row,
                                   text='Analyze', command=self._analyze)
        analyze_button.pack(side=tk.LEFT)
        next_button = tk.Button(second_row, text='+', command=self._next)
        next_button.pack(side=tk.RIGHT)
        prev_button = tk.Button(second_row, text='-', command=self._previous)
        prev_button.pack(side=tk.RIGHT)
        # third row: notification messages
        third_row = tk.Frame(base)
        third_row.pack(anchor=tk.N, expand=1, fill=tk.X)
        message_label = tk.Label(third_row)
        message_label.pack(side=tk.LEFT)
        parts['notification label'] = message_label
        # fourth row: text summary
        fourth_row = tk.Frame(base)
        fourth_row.pack(anchor=tk.N, expand=1, fill=tk.X)
        summary_label = tk.Label(fourth_row)
        summary_label.pack(side=tk.LEFT)
        parts['summary label'] = summary_label
        return parts

    def _create_board_image_cv(self, board=None):
        """Return a cv image of the board or empty board if not provided."""
        board = board or base.Board()  # empty board by default
        tile_h, tile_w = self._TILE_SHAPE[0:2]
        board_shape = tile_h * 8, tile_w * 8, 3
        board_image = numpy.zeros(board_shape, dtype=numpy.uint8)
        # place each tile on the image
        for (row, col), tile in board.positions_with_tile():
            tile_image = self._tile_images[tile._type]
            t, l = row * tile_h, col * tile_w
            b, r = t + tile_h, l + tile_w
            board_image[t:b, l:r] = tile_image
        return board_image

    def _draw_swap_cv(self, board_image, swap):
        """Add a white tile border to indicate the swap."""
        tile_h, tile_w = self._TILE_SHAPE[0:2]
        # get a single bounding box
        (row_1, col_1), (row_2, col_2) = swap
        t = tile_h * min(row_1, row_2)
        b = tile_h * (1 + max(row_1, row_2))
        l = tile_w * min(col_1, col_2)
        r = tile_w * (1 + max(col_1, col_2))
        top_left = (l, t)
        bottom_right = (r, b)
        data.cv2.rectangle(board_image, top_left, bottom_right,
                           color=(255, 255, 255), thickness = 4)

    def _convert_cv_to_tk(self, image_cv):
        """Convert an OpenCV image to a tkinter PhotoImage"""
        # convert BGR to RGB
        image_cv_rgb = data.cv2.cvtColor(image_cv, data.cv2.COLOR_BGR2RGB)
        # convert opencv to PIL
        image_pil = PIL_Image.fromarray(image_cv_rgb)
        # convert PIL to tkinter
        return ImageTk.PhotoImage(image_pil)

    def _analyze(self):
        """(Re)start analysis of the game on screen."""
        self._analyze_start_time = time.time()
        self._clear_ui()
        try:
            self._analysis_process.terminate()  # clear anything existing
        except AttributeError:  # there wasn't actually a process
            pass
        # self._analysis_process = _AsyncReadyFunction(self._analysis_function,
        #                                              None, 'async_results_q')
        out_q = mp.Queue()
        self._analysis_process = mp.Process(target=self._analysis_function,
                                            kwargs={'async_results_q': out_q})
        setattr(self._analysis_process, 'out_q', out_q)
        self._analysis_process.start()
        self._base.after(self._POLL_PERIOD_MILLISECONDS,
                         self._scheduled_check_for_summaries)
        self._update_notification('Analyzing the on-screen game.')

    def _scheduled_check_for_summaries(self):
        """Present the results if they have become available or timed out."""
        if self._analysis_process is None:
            return
        # handle time out
        timed_out = time.time() - self._analyze_start_time > self.time_limit
        if timed_out:
            self._handle_results('Analysis timed out but managed\n'
                                 ' to get lower turn results.',
                                 'Analysis timed out with no results.')
            return
        # handle standard completion
        try:
            self._analysis_process.join(0.001)
        except AssertionError:
            pass  # if some timing issue with closed process, just continue
        if not self._analysis_process.is_alive():
            self._handle_results('Completed analysis.',
                                 'Unable to find the game on screen.')
            return
        #finally, if it's still alive, then come back later
        self._base.after(self._POLL_PERIOD_MILLISECONDS,
                         self._scheduled_check_for_summaries)

    def _handle_results(self, success_message, failure_message):
        last_result = None
        while True:
            try:
                last_result = self._analysis_process.out_q.get(timeout=0.001)
            except QEmpty:
                break  # nothing left on the queue
        self.summaries = last_result
        if last_result:
            self._clear_ui()
            self._update_summary(self.summaries[0])
            self._update_notification(success_message)
        else:
            self._clear_ui()
            self._update_notification(failure_message)
        try:
            self._analysis_process.terminate()
        except AttributeError:
            pass  # just no process. ignore it.
        self._analysis_process = None

    def _next(self):
        """Get the next summary and present it."""
        self.summaries.rotate(-1)
        current_summary = self.summaries[0]
        self._update_summary(current_summary)

    def _previous(self):
        """Get the previous summary and present it."""
        self.summaries.rotate()
        current_summary = self.summaries[0]
        self._update_summary(current_summary)

    def _clear_ui(self):
        """Clear all messages and summaries from the UI."""
        self._update_notification()
        self._update_summary()

    def _update_notification(self, message=None):
        """Update the message area with blank or a message."""
        if message is None:
            message = ''
        message_label = self._parts['notification label']
        message_label.config(text=message)
        self._base.update()

    def _update_summary(self, summary=None):
        """Update all parts of the summary or clear when no summary."""
        board_image_label = self._parts['board image label']
        # get content for update or use blanks when no summary
        if summary:
            # make a board image with the swap drawn on it
            board, action, text = summary.board, summary.action, summary.text
            board_image_cv = self._create_board_image_cv(board)
            self._draw_swap_cv(board_image_cv, action)
            board_image_tk = self._convert_cv_to_tk(board_image_cv)
        else:
            #clear any stored state image and use the blank
            board_image_tk = board_image_label._blank_image
            text = ''
        # update the UI parts with the content
        board_image_label._board_image = board_image_tk
        board_image_label.config(image=board_image_tk)
        # update the summary text
        summary_label = self._parts['summary label']
        summary_label.config(text=text)
        # refresh the UI
        self._base.update()


if __name__ == "__main__":
    GUI()
