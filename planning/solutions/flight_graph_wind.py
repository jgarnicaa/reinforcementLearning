AIRCRAFT_SPEED = 500
WIND_SPEED = 50
WIND_DIRECTION = 90  # wind direction in the tangential plane


class FlightGraphWithWind(FlightGraph):

    def __init__(self, json_dict):
        super().__init__(json_dict)

    def generate_successors(
        self, node: Graph.Node
    ) -> List[Tuple[Graph.Node, float, str]]:
        for nwp, d in self._gotos[node.data].items():
            # Computes coordinates of the direction vector in the Earth-centered system
            dir_x = EARTH_RADIUS * (
                (cos(nwp.lat * pi / 180.0) * cos(nwp.long * pi / 180.0))
                - (cos(node.data.lat * pi / 180.0) * cos(node.data.long * pi / 180.0))
            )
            dir_y = EARTH_RADIUS * (
                (cos(nwp.lat * pi / 180.0) * sin(nwp.long * pi / 180.0))
                - (cos(node.data.lat * pi / 180.0) * sin(node.data.long * pi / 180.0))
            )
            dir_z = EARTH_RADIUS * (
                sin(nwp.lat * pi / 180.0) - sin(node.data.lat * pi / 180.0)
            )
            # Computes coordinates of the direction vector in the tangential plane at the waypoint node.data
            dir_a = (-dir_x * sin(node.data.long * pi / 180.0)) + (
                dir_y * cos(node.data.long * pi / 180.0)
            )
            dir_b = (
                (
                    dir_x
                    * (
                        -sin(node.data.lat * pi / 180.0)
                        * cos(node.data.long * pi / 180.0)
                    )
                )
                + (
                    dir_y
                    * (
                        -sin(node.data.lat * pi / 180.0)
                        * sin(node.data.long * pi / 180.0)
                    )
                )
                + (dir_z * cos(node.data.lat * pi / 180.0))
            )
            # Normalize the direction vector
            dir_na = dir_a / sqrt(dir_a * dir_a + dir_b * dir_b)
            dir_nb = dir_b / sqrt(dir_a * dir_a + dir_b * dir_b)
            # Compute wind vector in the tangential plane
            w_a = WIND_SPEED * sin(WIND_DIRECTION * pi / 180.0)
            w_b = WIND_SPEED * cos(WIND_DIRECTION * pi / 180.0)
            # Compute speed along direction vector
            mu = (dir_na * w_a) + (dir_nb * w_b)
            phi = (
                (mu * mu)
                - (WIND_SPEED * WIND_SPEED)
                + (AIRCRAFT_SPEED * AIRCRAFT_SPEED)
            )
            assert phi >= 0
            dir_speed = mu + sqrt(phi)
            assert dir_speed > 0
            flown_distance = (
                AIRCRAFT_SPEED * sqrt(dir_a * dir_a + dir_b * dir_b) / dir_speed
            )
            yield (
                Graph.Node(data=nwp, parent=node),
                flown_distance,
                str("GOTO {}".format(node.data)),
            )
