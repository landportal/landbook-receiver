from countries.fao_uri_resolver import FaoUriResolver

__author__ = 'guillermo'

from parser import Parser
from rdf_utils.namespaces_handler import *
from rdflib import Literal, XSD, URIRef
from rdflib.namespace import RDF, RDFS, FOAF
from countries.country_reader import CountryReader
from mimetypes import guess_type
import model.models as model
import datetime as dt
import sh
import os
import config
import inspect

class ReceiverRDFService(object):
    """
    Service that gets the _xml input from the html request, generates RDF triples and store
    them in Virtuoso triple store
    """

    def __init__(self, content):
        self.parser = Parser(content)
        self.time = dt.datetime.now()
	self.fao_resolver = FaoUriResolver() # Create an instance of FAO Resolver
        country_list_file = config.COUNTRY_LIST_FILE # path to the master file
	self.country_list = CountryReader().get_countries(country_list_file)

    def generate_rdf(self, graph, outputfile=None):
        """Generate RDF files

        :param graph: RDF graph.
        :param outputfile: Path for the output file.
        :returns: RDF graph.
        """
        print "Generating RDF"
	user_ip = "127.0.0.1" # TODO change it for a config setting
        bind_namespaces(graph)
	# Working
	self._add_landportal_triples(graph)
	self._add_licenses_triples(graph)
	self._add_organizations_triples(graph)
	self._add_indicators_triples(graph)
	self._add_observations_triples(graph)
	self._add_computation_triples(graph)
	self._add_area_triples_from_observations(graph)
	self._add_region_triples(graph)
	self._add_topics_triples(graph)
        self._add_data_source_triples(graph)
        self._add_users_triples(graph)
        self._add_upload_triples(graph, user_ip)
        self._add_dates_triples(graph)
        self._add_catalog_triples(graph)
        self._add_dataset_triples(graph)
        self._add_slices_triples(graph)
	# Next steps

	# Future
        # self._add_distribution_triples(graph)
        # self._add_area_triples_from_slices(graph)

        # dump the RDF graph to a file
        if outputfile is None:
           outputfile_rdf_xml = config.RDF_DATA_SET
        else:
           outputfile_rdf_xml = outputfile+".rdf"
        self._serialize_rdf_xml(graph, outputfile_rdf_xml)

        return graph


    def run_service(self, graph, host, api, graph_uri, user_ip, outputfile=None):
        """Run the ReceiverRDFService

        :param graph: RDF graph.
        :param graph_uri: RDF graph URI to be stored in the triple store.
        :param host: Triple store host.
        :param api: Triple store authentication api.
        :param user_ip: IP from the invoker client.
        :returns: RDF graph.
        """
        print "Running RDF service..."
        bind_namespaces(graph)
       # self._add_observations_triples(graph)
       # self._add_indicators_triples(graph)
       # self._add_area_triples_from_observations(graph)
       # self._add_area_triples_from_slices(graph)
       # self._add_computation_triples(graph)
       # self._add_data_source_triples(graph)
        self._add_catalog_triples(graph)
        self._add_dataset_triples(graph)
        self._add_distribution_triples(graph)
       # self._add_licenses_triples(graph)
       # self._add_organizations_triples(graph)
       # self._add_region_triples(graph)
       # self._add_slices_triples(graph)
       # self._add_upload_triples(graph, user_ip)
       # self._add_users_triples(graph)
       # self._add_topics_triples(graph)
       # self._add_dates_triples(graph)
	if outputfile is None:
	   outputfile_rdf_xml = config.RDF_DATA_SET
	   outputfile_turtle = config.TURTLE_DATA_SET
	else:
	   outputfile_rdf_xml = outputfile+".rdf"
	   outputfile_turtle = outputfile+".ttl"
        self._serialize_rdf_xml(graph, outputfile_rdf_xml)
        self._serialize_turtle(graph, outputfile_turtle)
        self._load_data_set(graph_uri=graph_uri, host=host, api=api)
        return graph


    def _add_landportal_triples(self, graph):
	print "Adding landportal.info ...."
	file_name = "../rdf_utils/landportal.info.rdf"
        basepath = os.path.dirname(__file__)
        filepath = os.path.abspath(os.path.join(basepath, file_name))
        graph.parse(location=filepath, format="application/rdf+xml")
        return graph


    def _add_catalog_triples(self, graph):
	print "Adding catalog..."
        lp_catalog = "catalog"
        dataset_id = self.parser.get_dataset().id
	catalog_url = base.term(lp_catalog)
	catalog_homepage = "http://landportal.info/data" # This URI could change
	landportal_url = "http://landportal.info"
	dataset_url = base_dataset.term(dataset_id)
        graph.add((catalog_url, RDF.type, dcat.term("Catalog")))
        graph.add((catalog_url, RDFS.label, Literal("Land Portal Catalog", lang="en")))
        graph.add((catalog_url, foaf.term("homepage"), URIRef(catalog_homepage)))
        graph.add((catalog_url, dcat.term("dataset"), dataset_url))
	graph.add((catalog_url, dct.term("publisher"), URIRef(landportal_url)))

        return graph

    def _add_dataset_triples(self, graph):
	print "Adding datasets..."
	# TODO add more information
        dataset = self.parser.get_dataset()
        lic = self.parser.get_license()
        dsource = self.parser.get_datasource()
	dataset_url = base_dataset.term(dataset.id)
        graph.add((dataset_url, RDF.type,
                   qb.term("DataSet")))
        graph.add((dataset_url, RDF.type,
                   dcat.term(Literal("Dataset"))))
        graph.add((dataset_url, sdmx_concept.term("freq"),
                   sdmx_code.term(dataset.sdmx_frequency)))
        graph.add((dataset_url, dct.term("accrualPeriodicity"),
                   sdmx_code.term(dataset.sdmx_frequency)))
        graph.add((dataset_url, lb.term("license"),
                   URIRef(lic.url)))
        graph.add((dataset_url, lb.term("dataSource"),
                   base_dsource.term(dsource.dsource_id)))
        graph.add((dataset_url, dct.term("issued"),
                   Literal(dt.datetime.now().strftime("%Y-%m-%d"),
                   datatype=XSD.date)))
        return graph

    def _add_distribution_triples(self, graph):
	print "Adding distribution..."
        file_name, file_extension = os.path.splitext(self.parser.get_file_name())
        file_extension = file_extension.replace(".", "")
        dataset_id = self.parser.get_dataset().id
        dist_id = dataset_id + "-" + file_extension
	dist_url = base_distribution.term(dist_id)
        file_type = guess_type(self.parser.get_file_name())
        file_size = os.path.getsize(config.RAW_FILE)

        graph.add((dist_url, RDF.type,
                   dcat.term("Distribution")))
        graph.add((dist_url, dcat.term("downloadURL"),
                   Literal(config.CKAN_INSTANCE + "dataset/" + dataset_id.lower())))
        graph.add((dist_url, dct.term("title"),
                   Literal(file_extension.upper() + " distribution of dataset " +
                           dataset_id, lang="en")))
        graph.add((dist_url, dcat.term("mediaType"),
                   Literal(file_type[0])))
        graph.add((dist_url, dcat.term("byteSize"),
                   Literal(file_size, datatype=XSD.decimal)))

        return graph

    def _add_dates_triples(self, graph):
        for obs in self.parser.get_observations():
            time_value = obs.ref_time
            term_object = base_time.term(time_value.value)
            graph.add((term_object,
                      RDF.type,
                      time.term('DateTimeInterval')))
            if isinstance(time_value, model.YearInterval):
                self._add_triples_of_year_interval(time_value, graph)

            elif isinstance(time_value, model.MonthInterval):
                self._add_triples_of_month_interval(time_value, graph)

            elif isinstance(time_value, model.Interval):
                self._add_triples_of_interval(time_value, graph)

            else:
                print "Unrecognized type of date: " + type(time_value)
        return graph

    def _add_triples_of_year_interval(self, time_object, graph):
        #base term
        term_object = base_time.term(time_object.value)

        #beginning and end
        graph.add((term_object,
                   time.term("hasBeginning"),
                   self._term_of_an_instant(time_object.year, 1, 1, graph)))
        graph.add((term_object,
                   time.term("hasEnd"),
                   self._term_of_an_instant(time_object.year, 12, 31, graph)))

        #DateTimeDescription
        date_time_desc_term = base_time.term(time_object.value + "_desc")
        graph.add((term_object,
                   time.term("hasDateTimeDescription"),
                   date_time_desc_term))
        graph.add((date_time_desc_term,
                   RDF.type,
                   time.term("DateTimeDescription")))
        graph.add((date_time_desc_term,
                   time.term("year"),
                   Literal(str(time_object.year), datatype=XSD.gYear)))
        graph.add((date_time_desc_term,
                   time.term("unitType"),
                   time.term("unitYear")))


    def _add_triples_of_month_interval(self, time_object, graph):
        #base term
        term_object = base_time.term(time_object.value)

        #beginning and end
        graph.add((term_object,
                   time.term("hasBeginning"),
                   self._term_of_an_instant(time_object.year, time_object.month, 1, graph)))
        graph.add((term_object,
                   time.term("hasEnd"),
                   self._term_of_an_instant(time_object.year, time_object.month, 31, graph)))
        #DateTimeDescription
        date_time_desc_term = base_time.term(time_object.value + "_desc")
        graph.add((term_object,
                   time.term("hasDateTimeDescription"),
                   time.term(date_time_desc_term)))
        graph.add((date_time_desc_term,
                   time.term("year"),
                   Literal(str(time_object.year), datatype=XSD.gYear)))
        graph.add((date_time_desc_term,
                   time.term("month"),
                   Literal("--" + str(time_object.month), datatype=XSD.gMonth)))
        graph.add((date_time_desc_term,
                   time.term("unitType"),
                   time.term("unitMonth")))


    def _add_triples_of_interval(self, time_object, graph):
        #base term
        term_object = base_time.term(time_object.value)

        #beginning and end
        graph.add((term_object,
                   time.term("hasBeginning"),
                   self._term_of_an_instant(time_object.start_time.year, 1, 1, graph)))
        graph.add((term_object,
                   time.term("hasEnd"),
                   self._term_of_an_instant(time_object.end_time.year, 12, 31, graph)))

    @staticmethod
    def _term_of_an_instant(year, month, day, graph):
        instant_term = base_time.term("instant_" + str(year) + "_" + str(month) + "_" + str(day))
        graph.add((instant_term,
                  RDF.type,
                  time.term("Instant")))
        graph.add((instant_term,
                  time.term("inXSDDateTime"),
                  Literal(str(year) + "-" + str(month) + "-" + str(day) + "T00:00:00Z", datatype=XSD.dateTime)))
        #2011-12-24T14:24:05Z

        return instant_term

    def _add_observations_triples(self, graph):
        """

        """
        print "Adding observations..."
        for obs in self.parser.get_observations():
            region = self._get_area_code(obs)
            obs_uri = generate_observation_uri(obs)
            graph.add((obs_uri, RDF.type,
                       qb.term("Observation")))
            graph.add((obs_uri, cex.term("ref-time"),
                       base_time.term(obs.ref_time.value)))
            graph.add((obs_uri, cex.term("ref-area"),
                       base_geo.term(region)))
            graph.add((obs_uri, cex.term("ref-indicator"),
                       base_ind.term(obs.indicator_id)))
            if not obs.value.obs_status == "obsStatus-M":
                if float(obs.value.value) % 1 != 0:
                    graph.add((obs_uri, cex.term("value"),
                              Literal(obs.value.value, datatype=XSD.double)))
                else:
                    graph.add((obs_uri, cex.term("value"),
                              Literal(int(float(obs.value.value)), datatype=XSD.integer)))
            graph.add((obs_uri, cex.term("computation"),
                       cex.term(str(obs.computation.uri))))
            graph.add((obs_uri, dct.term("issued"),
                       Literal(obs.issued.timestamp.strftime("%Y-%m-%d"),
                               datatype=XSD.date)))
            graph.add((obs_uri, qb.term("dataSet"),
                       base_dataset.term(obs.dataset_id)))

	    if obs.slice_id is not None:
               url_slice = generate_slice_uri_from_observation(obs)
	       graph.add((url_slice, qb.term("observation"), obs_uri))

            graph.add((obs_uri, RDFS.label,
                       Literal("Observation of " + str(region) +
                               " within the period of " + str(obs.ref_time.value) +
                               " for indicator " + str(obs.indicator_id), lang='en')))
            graph.add((obs_uri,
                       sdmx_concept.term("obsStatus"),
                       sdmx_code.term(obs.value.obs_status)))
        return graph

    @staticmethod
    def _get_literal_from_translations(element, attribute, lang_code):
	return getattr(next((x for x in element.translations if x.lang_code == lang_code), None), attribute)

    def _add_indicators_triples(self, graph):
        print "Adding indicators..."
        for ind in self.parser.get_simple_indicators():

	    # This is the way to access to the description in other languages, due to model constraint. Maybe in the future we can just add attributes
	    name_en = self._get_literal_from_translations(ind, "name","en")
	    name_fr = self._get_literal_from_translations(ind, "name","fr")
	    name_es = self._get_literal_from_translations(ind, "name","es")

	    description_en = self._get_literal_from_translations(ind, "description","en")
	    description_fr = self._get_literal_from_translations(ind, "description","fr")
	    description_es = self._get_literal_from_translations(ind, "description","es")

            graph.add((base_ind.term(ind.id), RDF.type,
                       cex.term("Indicator")))
            graph.add((base_ind.term(ind.id), lb.term("preferable_tendency"),
                       cex.term(ind.preferable_tendency)))
	    # TODO generate proper measurement triples
            graph.add((base_ind.term(ind.id), lb.term("measurement"),
                       Literal(ind.measurement_unit.name)))
            graph.add((base_ind.term(ind.id), lb.term("last_update"),
                       Literal(self.time.strftime("%Y-%m-%d"), datatype=XSD.date)))
            graph.add((base_ind.term(ind.id), lb.term("starred"),
                       Literal(ind.starred, datatype=XSD.Boolean)))
            graph.add((base_ind.term(ind.id), lb.term("topic"),
                       base_topic.term(ind.topic_id)))
            #graph.add((base_ind.term(ind.id), lb.term("indicatorType"),
            #           cex.term(ind.type)))
            graph.add((base_ind.term(ind.id), RDFS.label,
                       Literal(name_en, lang='en')))
            graph.add((base_ind.term(ind.id), RDFS.comment,
                       Literal(description_en, lang='en')))
            graph.add((base_ind.term(ind.id), RDFS.label,
                       Literal(name_fr, lang='fr')))
            graph.add((base_ind.term(ind.id), RDFS.comment,
                       Literal(description_fr, lang='fr')))
            graph.add((base_ind.term(ind.id), RDFS.label,
                       Literal(name_es, lang='es')))
            graph.add((base_ind.term(ind.id), RDFS.comment,
                       Literal(description_es, lang='es')))
        return graph

    def _add_slices_triples(self, graph):
        print "Adding slices..."
        for slc in self.parser.get_slices():
	    slice_url = generate_slice_uri(slc)
	    indicator_url = base_ind.term(str(slc.indicator_id))
	    dataset_url = base_dataset.term(slc.dataset_id)

            graph.add((slice_url, RDF.type,
                       qb.term("Slice")))
            graph.add((dataset_url, qb.term("slice"),
                       slice_url))
            graph.add((slice_url, cex.term("ref-indicator"),
                       indicator_url))

            if slc.region_code is not None:
                dimension = slc.region_code
            elif slc.country_code is not None:
                dimension = slc.country_code
            else:
                dimension = slc.dimension.value

            graph.add((slice_url, qb.term("dimension"),
                       base_dimension_area.term(dimension)))

        return graph

    def _add_users_triples(self, graph):
        print "Adding users..."
        user = self.parser.get_user()
        organization = self.parser.get_organization()
	user_url = base_user.term(user.id)
        graph.add((user_url, RDF.type, FOAF.Person))
        graph.add((user_url, RDFS.label, Literal(user.id, lang='en')))
        graph.add((user_url, FOAF.name, Literal(user.id)))
        graph.add((user_url, org.term("memberOf"), base_org.term(str(organization.id))))
        return graph

    def _add_organizations_triples(self, graph):
        print "Adding organization..."
        organization = self.parser.get_organization()

	# This is the way to access to the description in other languages, due to model constraint. Maybe in the future we can just add attributes
	description_en = self._get_literal_from_translations(organization, "description","en")
	description_fr = self._get_literal_from_translations(organization, "description","fr")
	description_es = self._get_literal_from_translations(organization, "description","es")


	organization_uri = base_org.term(organization.id)
        graph.add((organization_uri, RDF.type,
                   org.term("Organization")))
        graph.add((organization_uri, org.term("identifier"),
                   Literal(organization.acronym)))
        graph.add((organization_uri, RDFS.label,
                   Literal(organization.name, lang='en')))
        graph.add((organization_uri, FOAF.homepage,
                   URIRef(organization.url)))
        graph.add((organization_uri, RDFS.comment,
                   Literal(description_en, lang='en')))
        graph.add((organization_uri, RDFS.comment,
                   Literal(description_fr, lang='fr')))
        graph.add((organization_uri, RDFS.comment,
                   Literal(description_es, lang='es')))

        return graph

    def _add_topics_triples(self, graph):
	print "Adding topics..."
	file_name = "../rdf_utils/topics.rdf"
        basepath = os.path.dirname(__file__)
        filepath = os.path.abspath(os.path.join(basepath, file_name))
        graph.parse(location=filepath, format="application/rdf+xml")
        return graph

    def _add_area_triples_from_slices(self, graph):
        slices = self.parser.get_slices()
        for slc in slices:
            if slc.country_code:
                self._add_country(graph, slc)
            elif slc.region_code:
                self._add_region(graph, slc)
        return graph

    def _add_area_triples_from_observations(self, graph):
	print "Adding areas (country and regions) from observations..."
        observations = self.parser.get_observations()
	# Use set in order to only create triples the first time you find a new country or region
	country_set = set()
	region_set = set()
        for obs in observations:
            if obs.country_code not in country_set:
                self._add_country(graph, obs)
		country_set.add(obs.country_code)
            elif obs.region_code not in region_set:
                self._add_region(graph, obs)
		region_set.add(obs.region_code)
        return graph

    def _add_country(self, graph, arg):
	''' Add country triples into the graph. The country added is the one provided by the arg.country_code.
	Parameters
	----------
	graph : Graph
	   Graph.
	arg : 
	   Slice or observation with a country_code attribute.
	Returns:
	   The graph (with the new triples added)
	'''
        country_iso3 = arg.country_code

        country_id = ""
        country_name = ""
        iso2 = ""
        fao_uri = ""  # URL of the page
        region = ""
        fao_semantic_uri = ""  # Semantic uri node

	country = next((country for country in self.country_list if country_iso3 == country.iso3), None) # stop the first time there is a match

        country_name_en = self._get_literal_from_translations(country, "name", "en")
        country_name_es = self._get_literal_from_translations(country, "name", "es")
        country_name_fr = self._get_literal_from_translations(country, "name", "fr")
        country_iso2 = country.iso2
        country_fao_uri = country.faoURI
        region = country.is_part_of_id
        fao_semantic_uri = self.fao_resolver.get_URI_from_iso3(country_iso3)

        country_generated_url = base_geo.term(country_iso3)
        graph.add((country_generated_url, RDF.type, cex.term("Area")))
        graph.add((country_generated_url, RDF.type, lb.term("Country")))
        graph.add((country_generated_url, RDFS.label, Literal(country_name_en, lang="en")))
        graph.add((country_generated_url, RDFS.label, Literal(country_name_es, lang="es")))
        graph.add((country_generated_url, RDFS.label, Literal(country_name_fr, lang="fr")))
        graph.add((country_generated_url, lb.term("iso3"), Literal(country_iso3, datatype=XSD.string)))
        graph.add((country_generated_url, lb.term("iso2"), Literal(country_iso2, datatype=XSD.string)))
        graph.add((country_generated_url, lb.term("faoURI"), URIRef(country_fao_uri)))
        graph.add((country_generated_url, lb.term("is_part_of"), base_geo.term(region)))
        if fao_semantic_uri is not None:
            graph.add((country_generated_url, lb.term("faoReference"), URIRef(fao_semantic_uri)))
        return graph

    def _add_region_triples(self, graph):
	print "Adding regions..."
        self._add_region(graph, None)

    def _add_region(self, graph, arg):
	# TODO generate a static .rdf file with the triples and add to the graph
	# As far as there are the same triples all the time
	region_id_set = set()
        for country in self.country_list:
	    if country.is_part_of_id not in region_id_set:
	    	region_id_set.add(country.is_part_of_id)

	for region_id in region_id_set:
            region_URI = base_geo.term(region_id)
            graph.add((region_URI, RDF.type,
                       cex.term("Area")))
            graph.add((region_URI, RDF.type,
                       lb.term("Region")))
            graph.add((region_URI, RDFS.label,
                       Literal(region_id, lang="en")))
            un_code = None
            if region_id == "Americas":
                un_code = 19
            elif region_id == "Europe":
                un_code = 150
            elif region_id == "Oceania":
                un_code = 9
            elif region_id == "Africa":
                un_code = 2
            elif region_id == "Asia":
                un_code = 142
            elif region_id == "Antarctica":
                un_code = 10
            if un_code is not None:
	        graph.add((region_URI, lb.term("UNCode"), Literal(un_code,datatype=XSD.string)))

    @staticmethod
    def _get_area_code(arg):
        area = None
        if arg.country_code:
            area = arg.country_code
        elif arg.region_code:
            area = arg.region_code
        return area

    def _add_licenses_triples(self, graph):
        lic = self.parser.get_license()
	license_URL = URIRef(lic.url)

        graph.add((license_URL, RDF.type,
                   lb.term("License")))

        graph.add((license_URL, RDFS.label,
                   Literal(lic.name, lang="en")))

        graph.add((license_URL, RDFS.comment,
                   Literal(lic.description, lang="en")))

	graph.add((license_URL, foaf.term("page"),
                   URIRef(lic.url)))

	# TODO useful information to share?
	# graph.add((license_URL, lb.term("republish"),
	#           Literal(lic.republish, datatype=XSD.Boolean)))
        return graph

    def _add_computation_triples(self, graph):
	print "Adding computation..." 
	file_name = "../rdf_utils/computation.rdf"
        basepath = os.path.dirname(__file__)
        filepath = os.path.abspath(os.path.join(basepath, file_name))
        graph.parse(location=filepath, format="application/rdf+xml")

        return graph

    def _add_data_source_triples(self, graph):
	print "Adding DataSources..."
        data_source = self.parser.get_datasource()
        organization = self.parser.get_organization()
        user = self.parser.get_user()
        graph.add((base_dsource.term(data_source.dsource_id), RDF.type,
                   lb.term(Literal("DataSource"))))
        graph.add((base_dsource.term(data_source.dsource_id), RDFS.label,
                   Literal(data_source.name, lang='en')))
        graph.add((base_dsource.term(data_source.dsource_id), lb.term("organization"),
                   base_org.term(organization.id)))
	usr = self.parser.get_user()
        graph.add((base_dsource.term(data_source.dsource_id), dct.term("creator"), base_user.term(usr.id)))
        return graph

    def _add_upload_triples(self, graph, ip):
	print "Adding upload..."
	now = dt.datetime.now()
	timestamp = now.strftime("%Y-%m-%d")
        user = self.parser.get_user()
        dsource = self.parser.get_datasource()
        observations = self.parser.get_observations()
        upload_id = dsource.dsource_id + "-" + timestamp
        upload_url = base_upload.term(upload_id)
        graph.add((upload_url, RDF.type, lb.term(Literal("Upload"))))
        graph.add((upload_url, lb.term("user"), base_user.term(user.id)))
        graph.add((upload_url, lb.term("timestamp"), Literal(timestamp, datatype=XSD.date)))
        graph.add((upload_url, lb.term("ip"), Literal(ip, datatype=XSD.string)))
        for obs in observations:
            graph.add((upload_url, lb.term("observation"), generate_observation_uri(obs)))
        graph.add((upload_url, lb.term("dataSource"),
                   lb.term(dsource.dsource_id)))

        return graph

    @staticmethod
    def _serialize_rdf_xml(graph, filepath):
        serialized = graph.serialize(format='application/rdf+xml')
        with open(filepath, 'w') as dataset:
            dataset.write(serialized)
	    print "RDF/XML file generated at %s" %filepath

    @staticmethod
    def _serialize_turtle(graph, filepath):
        serialized = graph.serialize(format='turtle')
        with open(filepath, 'w') as dataset:
            dataset.write(serialized)
	    print "Turtle file generated at %s" %filepath

    @staticmethod
    def _load_data_set(host, api, graph_uri):
        sh.curl(host + api + graph_uri,
                digest=True, u=config.DBA_USER + ":" + config.DBA_PASSWORD,
                verbose=True, X="POST", T=config.RDF_DATA_SET)


