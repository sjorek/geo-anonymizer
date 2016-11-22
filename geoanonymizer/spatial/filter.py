# -*- coding: utf-8 -*-

u"""
Functions to filter spatial coordinates.

    “One variation on geographic masking is the use of additional spatial
    filters to ensure masked locations fall within predefined areas of
    interest.  For example, displacement could be limited to a physical land
    base by excluding surface water bodies (e.g., oceans, bays, rivers, and
    lakes) to ensure that no masked locations appear in areas which are
    obviously uninhabited.”

    -- from section 7 of `Ensuring Confidentiality of Geocoded Health Data:
    Assessing Geographic Masking Strategies for Individual-Level Data
    <https://www.hindawi.com/journals/amed/2014/567049/#sec7>`_

"""
