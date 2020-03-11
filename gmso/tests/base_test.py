import pytest
import numpy as np
import mbuild as mb
import unyt as u

from gmso.core.box import Box
from gmso.core.topology import Topology
from gmso.core.element import Hydrogen, Oxygen
from gmso.core.site import Site
from gmso.core.angle import Angle 
from gmso.core.atom_type import AtomType
from gmso.core.forcefield import ForceField
from gmso.external.convert_mbuild import from_mbuild
from gmso.tests.utils import get_path
from gmso.utils.io import get_fn


class BaseTest:
    @pytest.fixture(autouse=True)
    def initdir(self, tmpdir):
        tmpdir.chdir()

    @pytest.fixture
    def lengths(self):
        return u.nm * np.ones(3)

    @pytest.fixture
    def angles(self):
        return u.degree * [90, 90, 90]

    @pytest.fixture
    def charge(self):
        return u.elementary_charge * 1

    @pytest.fixture
    def mass(self):
        return 1 * u.gram/u.mol

    @pytest.fixture
    def box(self):
        return Box(lengths=u.nm*np.ones(3))

    @pytest.fixture
    def top(self):
        return Topology(name='mytop')

    @pytest.fixture
    def topology_site(self):
        def _topology(sites=1):
            top = Topology()
            top.box = Box(lengths=[1, 1, 1])
            H = Hydrogen
            for i in range(sites):
                site = Site(name='site1',
                             element=H,
                             atom_type=AtomType(name="at1",
                                                mass=H.mass),
                             )
                top.add_site(site)

            return top

        return _topology


    @pytest.fixture
    def ar_system(self):
        ar = mb.Compound(name='Ar')

        packed_system = mb.fill_box(
            compound=ar,
            n_compounds=100,
            box=mb.Box([3, 3, 3]),
        )

        return from_mbuild(packed_system)


    @pytest.fixture
    def typed_ar_system(self, ar_system):
        top = ar_system

        ff = ForceField(get_fn('ar.xml'))

        for site in top.sites:
            site.atom_type = ff.atom_types['Ar']

        top.update_topology()

        return top

    @pytest.fixture
    def water_system(self):
        water = mb.load(get_path('tip3p.mol2'))
        water.name = 'water'
        water[0].name = 'opls_111'
        water[1].name = water[2].name = 'opls_112'

        packed_system = mb.fill_box(
                compound=water,
                n_compounds=2,
                box=mb.Box([2, 2, 2])
                )

        return  from_mbuild(packed_system)

    @pytest.fixture
    def typed_water_system(self, water_system):
        top = water_system

        ff = ForceField(get_path('tip3p.xml'))

        element_map = {"O": "opls_111", "H": "opls_112"}

        for atom in top.sites:
            atom.atom_type = ff.atom_types[atom.name]

        for bond in top.bonds:
            bond.connection_type = ff.bond_types["opls_111~opls_112"]

        for subtop in top.subtops:
            angle = Angle(
                connection_members=[site for site in subtop.sites],
                name="opls_112~opls_111~opls_112",
                connection_type=ff.angle_types["opls_112~opls_111~opls_112"]
            )
            top.add_connection(angle)

        top.update_topology()

        return top
