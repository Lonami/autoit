ait
===

Automate it with Python.

What is this?
-------------

This Python 3 package aims to help you automate several GUI actions
easily through Python, like clicking, moving the mouse around, using
the keyboard, etc.

How to install it?
------------------

.. code-block::

    pip install autoit


External requirements?
----------------------

- Linux, for now.
- ``xdotool`` to do any ``ait`` operation.
- Python's ``Xlib`` to use ``ait.log`` (mouse/keyboard logger).


How does it look like?
----------------------

.. code-block:: python

    import ait

    # Click wherever the mouse is
    ait.click()

    # Click with the right mouse button
    ait.click('R')

    # Click at some position
    ait.click(140, 480)

    # Click in the center of the screen with the middle button
    ait.click(0.5, 0.5, 'M')

    # Click 10 pixels below
    ait.click(0j, 10j)

    # Movement (absolute, percentage and relative) can also be done
    ait.move(140, 480)
    ait.move(0.5, 0.5)
    ait.move(60j, -9j)

    # Mouse position can also be retrieved
    x, y = ait.mouse()

    # Pressing keys can also be done
    ait.press('q', '!', '\n')  # Exit vim
    ait.press(*'\b' * 10)  # 10 carriage returns

    # Writing things with the keyboard too
    ait.write('Hello world!\n')
