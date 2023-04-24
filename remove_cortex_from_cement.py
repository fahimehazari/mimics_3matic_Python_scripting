import mimics
''' This script removes the cortex from the cement mask, assuming ony that there is a mask named Cement'''

def wrap_and_smooth_from_mask(mask):
    part = mimics.segment.calculate_part(mask, 'Optimal')

    part = mimics.tools.wrap(part, smallest_detail=0.6, gap_closing_distance=0.5, dilate_result=True,
                             protect_thin_walls=False, keep_originals=False)
    part = mimics.tools.smooth(part, 0.4, iterations=5, compensate_shrinkage=False, keep_originals=False)
    return part

#Cortical mask
cort_m=mimics.segment.create_mask()
cort_m=mimics.segment.threshold(cort_m, 1686, 999999)
cort_m.name='Threshold'
cort_closed = mimics.segment.morphology_operations(cort_m,'Close',2,26,'Closed')
mimics.segment.smooth_mask(cort_closed)
mimics.segment.keep_largest(cort_closed)

#Cement mask
cement_p=mimics.data.parts.find('.*Cement.*',regex=True)
cement=mimics.segment.calculate_mask_from_part(cement_p, target_mask=None)
cement.name = 'Cement old'
cement_without_cortex=mimics.segment.boolean_operations(cement,cort_closed,'Minus')
cement_without_cortex_opened=mimics.segment.morphology_operations(cement_without_cortex,'Open',2,26,'Opened_cement')
mimics.segment.keep_largest(cement_without_cortex_opened)
cement_without_cortex_opened.name = 'Cement_without_cortex'

#Cement part
cement=wrap_and_smooth_from_mask(cement_without_cortex_opened)
cement.name='Cement'

#Delete parts
mimics.data.masks.delete(cort_m)
mimics.data.masks.delete(cort_closed)
mimics.data.masks.delete(cement_without_cortex)


#Closing 2 pix 26 - reg growing