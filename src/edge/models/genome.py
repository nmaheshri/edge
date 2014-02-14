from django.db import models
from edge.models.chunk import *
from edge.models.fragment import *
from edge.models.genome_updater import Genome_Updater


class Genome(models.Model, Genome_Updater):
    class Meta:
        app_label = "edge"

    name = models.CharField(max_length=256)
    parent = models.ForeignKey('self', null=True, on_delete=models.PROTECT)
    notes = models.TextField(null=True, blank=True)
    fragments = models.ManyToManyField(Fragment, through='Genome_Fragment')
    created_on = models.DateTimeField('Created', auto_now_add=True, null=True)

    def __unicode__(self):
        return self.name

    @staticmethod
    def create(name, notes=None):
        new_genome = Genome(name=name, notes=notes, parent=None)
        new_genome.save()
        return new_genome

    @staticmethod
    def import_gff(name, gff_fasta_fn):
        genome = Genome.create(name)
        from edge.importer import GFFImporter
        GFFImporter(genome, gff_fasta_fn).do_import()
        return genome

    def update(self, name=None, notes=None):
        name = self.name if name is None else name
        new_genome = Genome(name=name, notes=notes, parent=self)
        new_genome.save()
        for f in self.fragments.all():
            Genome_Fragment(genome=new_genome, fragment=f, inherited=True).save()
        return new_genome

    @property
    def has_location_index(self):
        for f in self.fragments.all():
            if not f.has_location_index:
                return False
        return True

    def indexed_genome(self):
        for f in self.fragments.all():
            f.indexed_fragment()
        # casting to Indexed_Genome
        return Indexed_Genome.objects.get(pk=self.pk)


class Indexed_Genome(Genome):
    """
    An Indexed_Genome is a Genome where each fragment has been indexed.
    """

    class Meta:
        app_label = "edge"
        proxy = True

    def find_annotation(self, name):
        q = Chunk_Feature.objects.filter(chunk__fragment_chunk_location__fragment__genome=self,
                                         feature__name=name)
        chunk_features = []
        for cf in q:
            # get fragment chunk location
            for fcl in Fragment_Chunk_Location.objects.filter(chunk=cf.chunk,
                                                              fragment__genome=self):
                chunk_features.append((cf, fcl))
        annotations = Annotation.from_chunk_feature_and_location_array(chunk_features)
        by_f = {}
        for annotation in annotations:
            if annotation.fragment.id not in by_f:
                by_f[annotation.fragment.id] = []
            by_f[annotation.fragment.id].append(annotation)
        return by_f

    def changes(self):
        if self.parent is None:
            return []

        edges = Edge.objects.filter(
            fragment__genome_fragment__genome=self,
            fragment__genome_fragment__inherited=False
        )

        fcs = []
        added = []
        for edge in edges:
            if edge.from_chunk:
                if edge.from_chunk.id not in added:
                    fcs.append(edge.fragment.indexed_fragment().fragment_chunk(edge.from_chunk))
                    added.append(edge.from_chunk.id)
            if edge.to_chunk:
                if edge.to_chunk.id not in added:
                    fcs.append(edge.fragment.indexed_fragment().fragment_chunk(edge.to_chunk))
                    added.append(edge.to_chunk.id)
        return fcs

    def changed_locations_by_fragment(self):
        changes = {}

        for c in self.changes():
            if c.fragment.id not in changes:
                changes[c.fragment.id] = []
            v = changes[c.fragment.id]
            if len(v) == 0 or v[-1][1]+1 != c.location[0]:
                v.append([c.location[0], c.location[1]])
            else:
                v[-1][1] = c.location[1]

        changes = {Fragment.objects.get(pk=f): v for f, v in changes.iteritems()}
        return changes


class Genome_Fragment(models.Model):
    class Meta:
        app_label = "edge"

    genome = models.ForeignKey(Genome)
    fragment = models.ForeignKey(Fragment)
    inherited = models.BooleanField()
