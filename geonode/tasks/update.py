from pprint import pprint
from celery.task import task
from geonode.geoserver.helpers import gs_slurp
from geonode.documents.models import Document
from geonode.cephgeo.models import CephDataObject, DataClassification
from geonode.cephgeo.utils import get_data_class_from_filename
from geonode.cephgeo.gsquery import nested_grid_update
#_fh
from geonode.layers.models import Layer
from geonode.base.models import TopicCategory

def layer_metadata(layer_list,flood_year,flood_year_probability):
    for layer in layer_list:
        #makati_city_fh5yr_10m_30m = Makati City Flood Hazard 5 Year Map
        #print "Old title: %s" % layer.title

        map_resolution = ''
        first_half = ''
        second_half = ''
        if "_10m_30m" in layer.title:
            map_resolution = '30'
        elif "_10m" in layer.title:
            map_resolution = '10'
        elif "_30m" in layer.title:
            map_resolution = '30'

        layer.title = layer.title.replace("_10m","").replace("_30m","").replace("__"," ").replace("_"," ").replace("fh%syr" % flood_year,"%s Year Flood Hazard Map" % flood_year).title()

        first_half = "This shapefile, with a resolution of %s meters, illustrates the inundation extents in the area if the actual amount of rain exceeds that of a %s year-rain return period." % (map_resolution,flood_year) + "\n\n" + "Note: There is a 1/" + flood_year + " (" + flood_year_probability + "%) probability of a flood with " +flood_year + " year return period occurring in a single year. \n\n"
        second_half = "3 levels of hazard:" + "\n" + "Low Hazard (YELLOW)" + "\n" + "Height: 0.1m-0.5m" + "\n\n" + "Medium Hazard (ORANGE)" + "\n" + "Height: 0.5m-1.5m" + "\n\n" + "High Hazard (RED)" + "\n" + "Height: beyond 1.5m"
        layer.abstract = first_half + second_half

        layer.purpose = " The flood hazard map may be used by the local government for appropriate land use planning in flood-prone areas and for disaster risk reduction and management, such as identifying areas at risk of flooding and proper planning of evacuation."

        layer.keywords.add("Flood Hazard Map")
        layer.category = TopicCategory.objects.get(identifier="geoscientificInformation")
        layer.save()

        print "Updated metadata for this layer: %s" % layer.title


@task(name='geonode.tasks.update.layers_metadata_update', queue='update')
def layers_metadata_update():
    # This will work for layer titles with the format '_fhXyr_'
    layer_list = Layer.objects.filter(title__icontains='fh5yr')
    layer_metadata(layer_list,'5','20')
    layer_list = Layer.objects.filter(title__icontains='fh25yr')
    layer_metadata(layer_list,'25','4')
    layer_list = Layer.objects.filter(title__icontains='fh100yr')
    layer_metadata(layer_list,'100','1')
    #problem: yung may enye
    #problem: 2 underscores



@task(name='geonode.tasks.update.ceph_metadata_udate', queue='update')
def ceph_metadata_udate(uploaded_objects):
    """
        NOTE: DOES NOT WORK
          Outputs error 'OperationalError: database is locked'
          Need a better way of making celery write into the database
    """
    #Save each ceph object
    for obj_meta_dict in uploaded_objects:
        ceph_obj = CephDataObject(  name = obj_meta_dict['name'],
                                    #last_modified = time.strptime(obj_meta_dict['last_modified'], "%Y-%m-%d %H:%M:%S"),
                                    last_modified = obj_meta_dict['last_modified'],
                                    size_in_bytes = obj_meta_dict['bytes'],
                                    content_type = obj_meta_dict['content_type'],
                                    data_class = get_data_class_from_filename(obj_meta_dict['name']),
                                    file_hash = obj_meta_dict['hash'],
                                    grid_ref = obj_meta_dict['grid_ref'])
        ceph_obj.save()

@task(name='geonode.tasks.update.grid_feature_update', queue='update')
def grid_feature_update(gridref_dict_by_data_class, field_value=1):
    """
        :param gridref_dict_by_data_class: contains mapping of [feature_attr] to [grid_ref_list]
        :param field_value: [1] or [0]
        Update the grid shapefile feature attribute specified by [feature_attr] on gridrefs in [gridref_list]
    """
    for feature_attr, grid_ref_list in gridref_dict_by_data_class.iteritems():
        nested_grid_update(grid_ref_list, feature_attr, field_value)

@task(name='geonode.tasks.update.geoserver_update_layers', queue='update')
def geoserver_update_layers(*args, **kwargs):
    """
    Runs update layers.
    """
    return gs_slurp(*args, **kwargs)


@task(name='geonode.tasks.update.create_document_thumbnail', queue='update')
def create_document_thumbnail(object_id):
    """
    Runs the create_thumbnail logic on a document.
    """

    try:
        document = Document.objects.get(id=object_id)

    except Document.DoesNotExist:
        return

    image = document._render_thumbnail()
    filename = 'doc-%s-thumb.png' % document.id
    document.save_thumbnail(filename, image)
