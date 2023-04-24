import mimics

''''This script takes the femur mask as input and creates a smooth part'''

fem = mimics.data.masks.find('.*Femur.*',regex=True)
fem.name='Femur'

def wrap_and_smooth_from_mask(mask):
    part = mimics.segment.calculate_part(mask, 'Optimal')

    part = mimics.tools.wrap(part, smallest_detail=0.6, gap_closing_distance=0.5, dilate_result=True,
                              protect_thin_walls=False, keep_originals=False)
    part = mimics.tools.smooth(part, 0.4, iterations=5, compensate_shrinkage=False, keep_originals=False)
    return part

part=wrap_and_smooth_from_mask(fem)
part.name = 'Femur'
