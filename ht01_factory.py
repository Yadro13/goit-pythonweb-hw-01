from abc import ABC, abstractmethod

# 1) Абстрактний базовий клас
class Vehicle(ABC):
    def __init__(self, make: str, model: str, spec: str = ""):
        self.make = make
        self.model = model
        self.spec = spec  # регіональна специфікація (наприклад, "US Spec", "EU Spec")

    @abstractmethod
    def start_engine(self) -> None:
        ...

    # Утиліта для красивої вивіски з урахуванням spec
    def _label(self) -> str:
        return f"{self.make} {self.model}{f' ({self.spec})' if self.spec else ''}"


# 2) Конкретні транспортні засоби
class Car(Vehicle):
    def start_engine(self) -> None:
        print(f"{self._label()}: Двигун запущено")


class Motorcycle(Vehicle):
    def start_engine(self) -> None:
        print(f"{self._label()}: Мотор заведено")


# 3) Абстрактна фабрика
class VehicleFactory(ABC):
    @abstractmethod
    def create_car(self, make: str, model: str) -> Car:
        ...

    @abstractmethod
    def create_motorcycle(self, make: str, model: str) -> Motorcycle:
        ...


# 4) Конкретні фабрики з регіональними специфікаціями
class USVehicleFactory(VehicleFactory):
    SPEC = "US Spec"

    def create_car(self, make: str, model: str) -> Car:
        return Car(make, model, self.SPEC)

    def create_motorcycle(self, make: str, model: str) -> Motorcycle:
        return Motorcycle(make, model, self.SPEC)


class EUVehicleFactory(VehicleFactory):
    SPEC = "EU Spec"

    def create_car(self, make: str, model: str) -> Car:
        return Car(make, model, self.SPEC)

    def create_motorcycle(self, make: str, model: str) -> Motorcycle:
        return Motorcycle(make, model, self.SPEC)


# 5) Використання фабрик
if __name__ == "__main__":
    us_factory = USVehicleFactory()
    eu_factory = EUVehicleFactory()

    vehicle1 = us_factory.create_car("Ford", "Mustang")
    vehicle1.start_engine()  # Ford Mustang (US Spec): Двигун запущено

    vehicle2 = eu_factory.create_motorcycle("BMW", "R nineT")
    vehicle2.start_engine()  # BMW R nineT (EU Spec): Мотор заведено

    # Легко додати інший регіон, не чіпаючи класи Car/Motorcycle:
    class JPVehFactory(VehicleFactory):
        SPEC = "JP Spec"
        def create_car(self, make, model): return Car(make, model, self.SPEC)
        def create_motorcycle(self, make, model): return Motorcycle(make, model, self.SPEC)

    jp_factory = JPVehFactory()
    vehicle3 = jp_factory.create_car("Toyota", "Corolla")
    vehicle3.start_engine()  # Toyota Corolla (JP Spec): Двигун запущено
