import numpy as np

from litter_assessment_service import preprocessing

class ClassificationResult:
    def __init__(self, image_data, image_name, model):
        self.image_data = image_data
        self.file_name = image_name
        self.model = model
        self.detected_classes = []
        self.c_matrix = []
        self.grid_shape = []

    def get_detected_classes(self):
        """
        returns lst of detected classes in the previously generated classification matrix.
        """
        if self.c_matrix==[]:
            raise AttributeError('Run get_c_matrix() to get classification matrix.')
        self.detected_classes = list(np.unique(self.c_matrix.astype('int64')))

class PLD_result(ClassificationResult):
    def __init__(self, *args):
        super().__init__(*args)
        self.get_c_matrix()
        self.get_detected_classes()

    def get_c_matrix(self):
        """
        performs classification for input tiles and saves the results as np.array
        """
        tile_size = 128
        image_tiles, shape_of_grid = preprocessing.get_image_tiles(self.image_data, tile_size)

        if isinstance(image_tiles, tuple):
            predictions = self.model.predict(image_tiles[0][(np.where(image_tiles[1] == 1))])
            classifications = np.zeros(shape_of_grid[0]*shape_of_grid[1])
            classifications[np.where(image_tiles[1] == 0)] = len(predictions[0])
            classifications[np.where(image_tiles[1] == 1)] = np.argmax(predictions, axis=1)
        if isinstance(image_tiles, np.ndarray):
            predictions = self.model.predict(image_tiles)
            classifications = np.argmax(predictions, axis=1)

        self.c_matrix = classifications.reshape(shape_of_grid)
        self.grid_shape = shape_of_grid

class PLQ_result(ClassificationResult):
    def __init__(self, PLD_c_matrix, *args):
        super().__init__(*args)
        self.PLD_c_matrix = PLD_c_matrix
        self.get_c_matrix()
        self.get_detected_classes()

    def scale_C_PLD(self, C, shape_of_grid_tuple):
        """
        doubles the amount if tiles by splitting them into two parts for quantification.
        """
        C_scaled = np.zeros(shape_of_grid_tuple)
        for i in range(len(C_scaled)- len(C_scaled)%2):
            for j in range(len(C_scaled[0])- len(C_scaled[0])%2):
                C_scaled[i,j] = C[(i//2), (j//2)]
        return C_scaled

    def polluted_area_helper(self, C_PLD, shape_of_grid):
        """
        returns np.array with 0 or 1 if tile was classified as polluted and -1 if it is not polluted.
        """
        c_polluted = self.scale_C_PLD(C_PLD, shape_of_grid)
        c_polluted = c_polluted.flatten()
        c_polluted[np.where(c_polluted > 1)] = -1 # non polluted. If PLQ wants to be looked at: change to 0
        c_polluted[np.where(c_polluted == 0)] =  1 # polluted
        c_polluted[np.where(c_polluted == 1)] =  1 # polluted
        return c_polluted

    def get_c_matrix(self):
        """
        performs classification for input tiles and saves the results as np.array
        """
        tile_size = 64
        image_tiles, shape_of_grid = preprocessing.get_image_tiles(self.image_data, tile_size)
        C_PLD_polluted = self.polluted_area_helper(self.PLD_c_matrix, shape_of_grid)#, X)
        predictions = []
        if np.where(C_PLD_polluted==1)[0] != []:
            if isinstance(image_tiles, tuple): # (X, alpha)
                predictions = self.model.predict(image_tiles[0][(np.where(C_PLD_polluted==1))])
            if isinstance(image_tiles, np.ndarray): # X
                predictions = self.model.predict(image_tiles[(np.where(C_PLD_polluted==1))])
        output_dim = self.model.compute_output_shape((1, tile_size, tile_size,3))
        C_PLD_polluted[np.where(C_PLD_polluted == -1)] = output_dim[1]
        if predictions != []:
            classifications = np.argmax(predictions, axis=1)
            C_PLD_polluted[np.where(C_PLD_polluted == 1)] = classifications
        elif predictions != []:
            C_PLD_polluted[np.where(C_PLD_polluted == 1)] = output_dim[1]
        self.c_matrix = C_PLD_polluted.reshape(shape_of_grid)
        self.grid_shape = shape_of_grid
